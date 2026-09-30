from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "todos.db"

app = Flask(__name__)
app.secret_key = "internspark-demo-secret"

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

@app.route("/")
def index():
    db = get_db()
    todos = db.execute("SELECT * FROM todos ORDER BY completed ASC, id DESC").fetchall()
    db.close()
    return render_template("index.html", todos=todos)

@app.post("/add")
def add_todo():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title cannot be empty.", "warning")
        return redirect(url_for("index"))

    db = get_db()
    db.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    db.commit()
    db.close()
    flash("Task added successfully.", "success")
    return redirect(url_for("index"))

@app.post("/toggle/<int:todo_id>")
def toggle_todo(todo_id):
    db = get_db()
    db.execute("""
        UPDATE todos
        SET completed = CASE completed WHEN 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (todo_id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.post("/delete/<int:todo_id>")
def delete_todo(todo_id):
    db = get_db()
    db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    db.close()
    flash("Task deleted.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
