from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

@auth.route('/logout')
def logout():
    pass