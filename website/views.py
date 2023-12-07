from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return '<h1>Foo</h1>'


@views.route('/add')
def add():
    pass

