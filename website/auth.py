from flask import Blueprint, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not username:
            flash("Please enter a username!", category="error")
        elif len(username) < 5:
            flash("Username must be at least 5 characters!", category="error")
        elif not password1:
            flash("Please enter a password!", category="error")
        elif len(password1) < 5:
            flash("Password must be at least 5 characters!", category="error")
        elif not password2:
            flash("Please confirm password!", category="error")
        elif password2 != password1:
            flash("Passwords do not match!", category="error")
    else:
        return render_template("register.html")

@auth.route('/logout')
def logout():
    pass