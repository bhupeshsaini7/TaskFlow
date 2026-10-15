from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from mysql.connector import Error as MySQLError

import db
from config import Config

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

VALID_STATUSES = ("Pending", "Completed")


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def validate_task_form(form):
    """Clean and check the submitted form.

    Returns (values, due_date, errors):
      values   - cleaned text, used to refill the form if there are errors
      due_date - a real date object (or None)
      errors   - a list of messages to show the user
    """
    title = " ".join(form.get("title", "").split())
    description = form.get("description", "").strip()
    due_raw = form.get("due_date", "").strip()
    status = form.get("status", "Pending")

    errors = []
    due_date = None

    if not title:
        errors.append("Title is required.")
    elif len(title) > 100:
        errors.append("Title must be 100 characters or fewer.")

    if len(description) > 1000:
        errors.append("Description must be 1000 characters or fewer.")

    if due_raw:
        try:
            due_date = datetime.strptime(due_raw, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Due date is not a valid date.")

    if status not in VALID_STATUSES:
        errors.append("Status must be Pending or Completed.")

    values = {
        "title": title,
        "description": description,
        "due_date": due_raw,
        "status": status,
    }
    return values, due_date, errors


def get_task_or_404(task_id):
    task = db.fetch_one("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    if task is None:
        abort(404)
    return task


# ---------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------
@app.route("/")
def dashboard():
    counts = db.fetch_one(
        """
        SELECT COUNT(*) AS total,
               COALESCE(SUM(status = 'Pending'), 0)   AS pending,
               COALESCE(SUM(status = 'Completed'), 0) AS completed
        FROM tasks
        """
    )
    total = int(counts["total"])
    pending = int(counts["pending"])
    completed = int(counts["completed"])
    percent_done = round(completed * 100 / total) if total > 0 else 0

    upcoming = db.fetch_all(
        """
        SELECT task_id, title, due_date
        FROM tasks
        WHERE status = 'Pending'
        ORDER BY due_date IS NULL, due_date, task_id
        LIMIT 5
        """
    )

    return render_template(
        "dashboard.html",
        total=total,
        pending=pending,
        completed=completed,
        percent_done=percent_done,
        upcoming=upcoming,
        today=date.today(),
    )


# ---------------------------------------------------------------
# Tasks: list, add, edit, toggle status, delete
# ---------------------------------------------------------------
@app.route("/tasks")
def list_tasks():
    tasks = db.fetch_all(
        """
        SELECT task_id, title, description, due_date, status
        FROM tasks
        ORDER BY status = 'Completed', due_date IS NULL, due_date, task_id DESC
        """
    )
    return render_template("tasks.html", tasks=tasks, today=date.today())


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        values, due_date, errors = validate_task_form(request.form)
        if not errors:
            db.execute(
                """INSERT INTO tasks (title, description, due_date, status)
                   VALUES (%s, %s, %s, 'Pending')""",
                (values["title"], values["description"] or None, due_date),
            )
            flash("Task added successfully.", "success")
            return redirect(url_for("list_tasks"))
        return render_template("task_form.html", form=values, errors=errors, mode="add")

    return render_template("task_form.html", form={}, errors=[], mode="add")


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task_or_404(task_id)

    if request.method == "POST":
        values, due_date, errors = validate_task_form(request.form)
        if not errors:
            db.execute(
                """UPDATE tasks
                   SET title = %s, description = %s, due_date = %s, status = %s
                   WHERE task_id = %s""",
                (values["title"], values["description"] or None,
                 due_date, values["status"], task_id),
            )
            flash("Task updated successfully.", "success")
            return redirect(url_for("list_tasks"))
        return render_template("task_form.html", form=values, errors=errors, mode="edit")

    return render_template("task_form.html", form=task, errors=[], mode="edit")


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    task = get_task_or_404(task_id)
    new_status = "Completed" if task["status"] == "Pending" else "Pending"
    db.execute("UPDATE tasks SET status = %s WHERE task_id = %s", (new_status, task_id))
    flash(f"Task marked as {new_status}.", "success")
    return redirect(request.referrer or url_for("list_tasks"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    get_task_or_404(task_id)
    db.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    flash("Task deleted.", "success")
    return redirect(url_for("list_tasks"))


# ---------------------------------------------------------------
# Error pages
# ---------------------------------------------------------------
@app.errorhandler(MySQLError)
def handle_database_error(error):
    # Details go to the terminal, not to the visitor.
    app.logger.error("Database error: %s", error)
    return (
        render_template(
            "error.html",
            title="Database problem",
            message="Something went wrong talking to the database. "
                    "Check that MySQL is running and that your .env settings are correct.",
        ),
        500,
    )


@app.errorhandler(404)
def handle_not_found(error):
    return (
        render_template(
            "error.html",
            title="Page not found",
            message="The page or task you asked for does not exist.",
        ),
        404,
    )


if __name__ == "__main__":
    # debug=True is for local learning only. Never use it on a public server.
    app.run(debug=True)