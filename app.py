from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"

def connect():
    return sqlite3.connect("database.db")

def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        service TEXT,
        date TEXT,
        time TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("SELECT * FROM users")
    if not c.fetchall():
        c.execute("INSERT INTO users VALUES (NULL,'admin','1234','admin')")
        c.execute("INSERT INTO users VALUES (NULL,'master','1234','master')")

    conn.commit()
    conn.close()

init_db()

# --- ГЛАВНАЯ ---
@app.route("/")
def index():
    return render_template("index.html")

# --- ПОЛУЧИТЬ ЗАНЯТЫЕ СЛОТЫ ---
@app.route("/slots")
def slots():
    date = request.args.get("date")

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT time FROM bookings WHERE date=?", (date,))
    times = [row[0] for row in c.fetchall()]

    conn.close()
    return jsonify(times)

# --- ЗАПИСЬ ---
@app.route("/book", methods=["POST"])
def book():
    data = request.form

    conn = connect()
    c = conn.cursor()

    # проверка занятости
    c.execute("SELECT * FROM bookings WHERE date=? AND time=?",
              (data["date"], data["time"]))

    if c.fetchone():
        return "Время уже занято!"

    c.execute("INSERT INTO bookings VALUES (NULL,?,?,?,?,?)",
              (data["name"], data["phone"], data["service"], data["date"], data["time"]))

    conn.commit()
    conn.close()

    return redirect("/")

# --- LOGIN ---
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = connect()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()

        if user:
            session["user"] = u
            session["role"] = user[3]
            return redirect("/admin")

    return render_template("login.html")

# --- АДМИНКА ---
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM bookings ORDER BY date,time")
    bookings = c.fetchall()

    conn.close()

    return render_template("admin.html", bookings=bookings, role=session["role"])

# --- УДАЛЕНИЕ ---
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "Нет доступа"

    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

app.run(debug=True)
