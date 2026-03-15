from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import pickle
import numpy as np
import datetime

app = Flask(__name__)
app.secret_key = "mentalhealth_secret"

# Load ML model
model = pickle.load(open("model.pkl", "rb"))


# Database connection
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create tables if they do not exist
def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        severity TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# Home route
@app.route("/")
def home():
    return redirect("/login")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        conn.execute(
            "INSERT INTO users(email,password) VALUES(?,?)",
            (email, password)
        )
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:

            session["user_id"] = user["id"]

            return redirect("/dashboard")

        else:

            error = "Username or Password Incorrect"

    return render_template("login.html", error=error)


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# API for progress chart (NO JINJA USED)
@app.route("/get_progress")
def get_progress():

    if "user_id" not in session:
        return jsonify({"scores": [], "dates": []})

    conn = get_db()

    data = conn.execute(
        "SELECT score,date FROM scores WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    scores = [row["score"] for row in data]
    dates = [row["date"] for row in data]

    return jsonify({
        "scores": scores,
        "dates": dates
    })


# Test page
@app.route("/test")
def test():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("test.html")


# ML prediction
@app.route("/predict", methods=["POST"])
def predict():

    responses = request.json["responses"]

    arr = np.array(responses).reshape(1, -1)

    severity = model.predict(arr)[0]

    score = sum(responses)

    conn = get_db()

    conn.execute(
        "INSERT INTO scores(user_id,score,severity,date) VALUES(?,?,?,?)",
        (
            session["user_id"],
            score,
            severity,
            str(datetime.date.today())
        )
    )

    conn.commit()

    return jsonify({
        "severity": severity,
        "score": score
    })


# Chatbot
@app.route("/chatbot", methods=["POST"])
def chatbot():

    message = request.json["message"].lower()

    if "sad" in message:
        reply = "I'm sorry you're feeling sad. Talking to a friend or therapist may help."

    elif "stress" in message:
        reply = "Stress can sometimes be reduced with breathing exercises or short walks."

    elif "anxious" in message:
        reply = "Try slow breathing. Inhale for 4 seconds and exhale slowly."

    elif "depressed" in message:
        reply = "You are not alone. Consider reaching out to someone you trust."

    elif "hello" in message or "hi" in message:
        reply = "Hello! How are you feeling today?"

    else:
        reply = "I'm here to listen. Tell me more about how you're feeling."

    return jsonify({"reply": reply})


# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/result")
def result():
    score = request.args.get("score")
    severity = request.args.get("severity")
    return render_template("result.html", score=score, severity=severity)

@app.route("/therapists")
def therapists():
    return render_template("therapists.html")


if __name__ == "__main__":
    app.run(debug=True)