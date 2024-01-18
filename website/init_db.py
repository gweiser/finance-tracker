import sqlite3

db = sqlite3.connect('database.db')


# with open("schema.sql") as f:
#     db.executescript(f.read())

db.executescript("""
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

    DROP TABLE IF EXISTS loan_to;             

    CREATE TABLE loan_to (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        person TEXT NOT NULL,
        creation_date date NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)  
    );

    DROP TABLE IF EXISTS bin;

    CREATE TABLE bin (
        id INTEGER PRIMARY KEY,
        amount INTEGER NOT NULL,
        note TEXT NOT NULL,
        expense_location TEXT NOT NULL,
        expense_date TEXT NOT NULL,
        user_id INTEGER NOT NULL
    );

     """ 
     )


db.commit() 
db.close()