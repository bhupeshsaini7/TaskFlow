# TaskFlow

A simple task manager built with Python, Flask, MySQL and Bootstrap 5.

## Features
- Add tasks with a title, description and due date
- View all tasks, edit them, delete them
- Mark tasks as Pending or Completed
- Dashboard with total, pending and completed counts

## Requirements
- Windows 10/11
- Python 3.9 or newer
- MySQL Server 8.x
- VS Code (recommended)

## Setup (Windows)

### 1. Open the project
Open the `taskflow` folder in VS Code, then open the terminal (Ctrl + `).

### 2. Create a virtual environment and install packages
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell blocks activation, run this once, then activate again:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Create the database and table
Run from inside the project folder:
```
mysql -u root -p -e "source schema.sql"
```
Enter your MySQL root password when asked.

### 4. Create a MySQL user for the app
```
mysql -u root -p
```
Then type (choose your own password):
```
CREATE USER 'taskflow_user'@'localhost' IDENTIFIED BY 'choose_a_strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON taskflow.* TO 'taskflow_user'@'localhost';
EXIT;
```

### 5. Create your .env file
```
copy .env.example .env
```
Open `.env` and fill in `DB_PASSWORD` (the password from step 4) and `SECRET_KEY`.
Generate a secret key with:
```
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the app
```
python app.py
```
Open http://127.0.0.1:5000 in your browser. Stop the server with Ctrl + C.

## Testing checklist
1. Dashboard shows 0 / 0 / 0 on an empty database.
2. Add a task: it appears in All Tasks and the dashboard total increases.
3. Try adding a task with an empty title: you get an error message.
4. Edit a task: changes are saved.
5. Click "Mark Completed": status changes and dashboard counts update.
6. Click "Mark Pending": it moves back.
7. Delete a task (confirm the popup): it disappears.

## Troubleshooting
- `mysql` is not recognized: add MySQL's `bin` folder (for example
  `C:\Program Files\MySQL\MySQL Server 8.0\bin`) to your PATH, or run the
  schema file in MySQL Workbench instead (File > Open SQL Script > run).
- Access denied for user: check DB_USER and DB_PASSWORD in `.env`.
- Unknown database 'taskflow': run step 3 again.
- Missing environment variable: you have not created `.env` (step 5).

## Security notes
- Secrets live in `.env`, which is ignored by Git.
- All SQL uses parameterized queries.
- This project has no login and no CSRF protection. That is fine for local
  learning. Add Flask-WTF and user accounts before putting it online.