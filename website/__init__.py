from flask import Flask
from flask_session import Session
from os import path
import sqlite3

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'very very secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    
    Session(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    
    return app 


# Connect to database
def get_db_connection():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn