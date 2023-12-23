from flask import Flask, Blueprint, render_template, request, flash, session, redirect, url_for
from website import get_db_connection
from hashlib import pbkdf2_hmac

views = Blueprint('views', __name__)

# Connect to database
db = get_db_connection()

@views.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check for user not existing
        if db.execute("SELECT 1 from users WHERE LOWER(username) = LOWER(?)", (username, )).fetchone() is None:
            flash("Username does not exist", "error")
        # If user exists
        else:    
            # Get row from database
            hashed_pwd_row = db.execute("SELECT hashed_pwd FROM users WHERE username = ?", (username, )).fetchone()
            # Index into the hashed_pwd for that row
            hashed_pwd_string = hashed_pwd_row["hashed_pwd"]

            # hash user input (for comparing to database hash)
            input_hashed = pbkdf2_hmac("sha256", password.encode(), b"bad_salt", 200_000)
            input_hashed_string = input_hashed.hex()

            # If passwords don't match
            if hashed_pwd_string != input_hashed_string:
                flash("Password is incorrect!", "error")
            # If passwords match
            else:
                # Store user in session
                session["username"] = username
                flash(f"Welcome, {username}!", "success")
                # Send user to main page
                return redirect(url_for("views.home"))
            
        # Bring user back to login
        return redirect(url_for("views.login"))
    else:
        return render_template("login.html")


@views.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":        
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not username:
            flash("Please provide a username!", "error")
        # Check if user already in database 
        elif db.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username, )).fetchone() is not None:
            flash("Username already exists!", "error")
        elif len(username) < 5:
            flash("Username must be at least 5 characters!", "error")
        elif not password1:
            flash("Please provide password", "error")
        elif len(password1) < 3:
            flash("Password must be at least 3 characters long!", "error")
        elif not password2:
            flash("Please confirm your password!", "error")
        elif password2 != password1:
            flash("Passwords do not match!", "error")
        else:
            # hash password, then convert it to string 
            hashed_pwd = pbkdf2_hmac("sha256", password1.encode(), b"bad_salt", 200_000)
            hashed_pwd_string = hashed_pwd.hex()
            db.execute("INSERT INTO users (username, hashed_pwd) VALUES (?, ?)", (username, hashed_pwd_string))
            db.commit()
            flash("Account created successfully!", "success")
            # Redirect user to login page
            return redirect(url_for("views.login"))
        
    return render_template("register.html")


@views.route('/logout', methods = ["GET", "POST"])
def logout():
    session["username"] = None
    flash("Logged out!", "success")
    return redirect(url_for("views.login"))    


@views.route('/', methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        if session["username"] is not None:
            return render_template("home.html")
        else:
            return redirect(url_for("views.login"))

@views.route('/add')
def add():
    pass

