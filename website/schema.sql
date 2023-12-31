DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id int NOT NULL PRIMARY KEY,
    username varchar(250) NOT NULL,
    hashed_pwd varchar(250) NOT NULL
    );


DROP TABLE IF EXISTS expenses;

CREATE TABLE expenses (
    id int NOT NULL PRIMARY KEY,
    amount int NOT NULL,
    note varchar(250) NOT NULL,
    expense_location varchar(250) NOT NULL,
    expense_date date NOT NULL,
    user_id int NOT NULL FOREIGN KEY REFERENCES users(id)
);