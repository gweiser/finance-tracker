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
        print(username)
        print(password1)
        print(password2)
        flash("Form submitted succesfully!")
        if not username:
            pass
        elif len(username) < 5:
            pass
        elif not password1:
            pass
        elif len(password1) < 5:
            pass
        elif not password2:
            pass
        elif password2 != password1:
            pass

    return render_template("register.html")

@auth.route('/logout')
def logout():
    pass