from flask import Flask, Blueprint, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

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

        user = User.query.filter_by(username=username)
        if user:
            flash("User already exists", "error")
        elif not username:
            flash("Please provide a username!", "error")
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

        new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
    
    return render_template("register.html")

@auth.route('/logout')
def logout():
    pass