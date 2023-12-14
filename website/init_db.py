import sqlite3

connection = sqlite3.connect('database.db')


# with open("schema.sql") as f:
#     connection.executescript(f.read())

connection.executescript("""
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        hashed_pwd TEXT NOT NULL
        );


    DROP TABLE IF EXISTS expenses;

    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        note TEXT NOT NULL,
        expense_location TEXT NOT NULL,
        expense_date date NOT NULL,
        user_id INTEGER NOT NULL,                         
        FOREIGN KEY(user_id) REFERENCES users(id)
    );      
                   """)


connection.commit() 
connection.close()