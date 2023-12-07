from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    pass

@auth.route('/register')
def register():
    pass

@auth.route('/logout')
def logout():
    pass