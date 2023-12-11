from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'very very secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    
    from .models import User, Expense

    # Create Database
    with app.app_context():
        db.create_all()


    return app 

def create_database():
    if not path.exists("website/" + DB_NAME):
        db.create_all()
        print("Created Database!")