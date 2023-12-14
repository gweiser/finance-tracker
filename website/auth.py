from flask import Flask, Blueprint, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from website import get_db_connection

auth = Blueprint('auth', __name__)

# Connect to database
db = get_db_connection()

@auth.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":        
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        users = db.execute("SELECT username FROM users").fetchall()

        print(*users)
        if not username:
            flash("Please provide a username!", "error")
        elif username in users:
            flash("Username already exists!", "error")
        elif len(username) < 5:
            flash("Username must be at least 5 characters!", "error")
        elif not password1:
            flash("Please provide password", "error")
        elif len(password1) < 5:
            flash("Password must be at least 5 characters long!", "error")
        elif not password2:
            flash("Please confirm your password!", "error")
        elif password2 != password1:
            flash("Passwords do not match!", "error")
        else:
            hashed_pwd = generate_password_hash(password1, "pbkdf2:sha256")
            db.execute("INSERT INTO users (username, hashed_pwd) VALUES (?, ?)", (username, hashed_pwd))
            db.commit()
            flash("Account created successfully!", "success")
        
    return render_template("register.html")

@auth.route('/logout')
def logout():
    pass