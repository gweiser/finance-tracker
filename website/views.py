from flask import Flask, Blueprint, render_template, request, flash, session, redirect, url_for
from website import get_db_connection
from hashlib import pbkdf2_hmac

views = Blueprint('views', __name__)

# Connect to database
db = get_db_connection()

@views.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check for user not existing
        if db.execute("SELECT 1 from users WHERE LOWER(username) = LOWER(?)", (username, )).fetchone() is None:
            flash("Username does not exist", "error")
        # If user exists
        else:    
            # Get row from database
            hashed_pwd_row = db.execute("SELECT hashed_pwd FROM users WHERE username = ?", (username, )).fetchone()
            # Index into the hashed_pwd for that row
            hashed_pwd_string = hashed_pwd_row["hashed_pwd"]

            # hash user input (for comparing to database hash)
            input_hashed = pbkdf2_hmac("sha256", password.encode(), b"bad_salt", 200_000)
            input_hashed_string = input_hashed.hex()

            # If passwords don't match
            if hashed_pwd_string != input_hashed_string:
                flash("Password is incorrect!", "error")
            # If passwords match
            else:
                # Store user in session
                session["username"] = username
                flash(f"Welcome, {username}!", "success")
                # Send user to main page
                return redirect(url_for("views.home"))
            
        # Bring user back to login
        return redirect(url_for("views.login")) 
    else:
        return render_template("login.html")


@views.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":        
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not username:
            flash("Please provide a username!", "error")
        # Check if user already in database 
        elif db.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username, )).fetchone() is not None:
            flash("Username already exists!", "error")
        elif len(username) < 5:
            flash("Username must be at least 5 characters!", "error")
        elif not password1:
            flash("Please provide password", "error")
        elif len(password1) < 3:
            flash("Password must be at least 3 characters long!", "error")
        elif not password2:
            flash("Please confirm your password!", "error")
        elif password2 != password1:
            flash("Passwords do not match!", "error")
        else:
            # hash password, then convert it to string 
            hashed_pwd = pbkdf2_hmac("sha256", password1.encode(), b"bad_salt", 200_000)
            hashed_pwd_string = hashed_pwd.hex()
            db.execute("INSERT INTO users (username, hashed_pwd) VALUES (?, ?)", (username, hashed_pwd_string))
            db.commit()
            flash("Account created successfully!", "success")
            # Redirect user to login page
            return redirect(url_for("views.login"))
        
    return render_template("register.html")


@views.route('/logout', methods = ["GET", "POST"])
def logout():
    if session["username"] is not None:
        # Remove username from session and redirect to login page
        username = session["username"]
        session["username"] = None
        flash(f"Goodbye, {username}", "success")
        return redirect(url_for("views.login"))    
    else:
        return redirect(url_for("views.login"))


@views.route('/', methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        if session["username"] is not None:
            current_user = session["username"]
            current_user_id_row = db.execute("SELECT id FROM users WHERE username = ?", (current_user, )).fetchone()
            current_user_id = current_user_id_row["id"]
            expenses_row = db.execute("SELECT * FROM expenses WHERE user_id = ?", (current_user_id, )).fetchall()
            loans_to_row = db.execute("SELECT * FROM loan_to WHERE user_id = ?", (current_user_id, )).fetchall()
            # Get all expenses
            expenses = []
            expense_counter = 0
            for _ in expenses_row:
                expenses.append({"amount": expenses_row[expense_counter]["amount"], 
                                 "note": expenses_row[expense_counter]["note"],
                                 "location": expenses_row[expense_counter]["expense_location"],
                                 "date": expenses_row[expense_counter]["expense_date"],
                                 "id": expenses_row[expense_counter]["id"]})
                expense_counter+=1

            loans_to = []
            loans_to_counter = 0
            for _ in loans_to_row:
                loans_to.append({"amount": loans_to_row[loans_to_counter]["amount"],
                                 "person": loans_to_row[loans_to_counter]["person"],
                                 "note": loans_to_row[loans_to_counter]["note"],
                                 "creation_date": loans_to_row[loans_to_counter]["creation_date"],
                                 "return_date": loans_to_row[loans_to_counter]["return_date"],
                                 "id": loans_to_row[loans_to_counter]["id"]})
                loans_to_counter+=1

                
            return render_template("home.html", expenses=expenses, loans_to=loans_to)
        else:
            return redirect(url_for("views.login"))


@views.route('/expense', methods = ["GET", "POST"])
@views.route("/expense/edit/<int:id>", methods=["GET", "POST"])
def expense(id=None):
    if session["username"] is not None:
        data = None
        user_id_row = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()
        user_id = user_id_row["id"]

        # if edit button is pressed (if an id is inputted)
        if id is not None:
            if request.method == "GET":
                data = db.execute("SELECT * FROM expenses WHERE id = ?", (id, )).fetchone()

                return render_template("expense.html", data=data)
            else:
                db.execute("DELETE FROM expenses WHERE id = ?", (id, ))

                amount = request.form.get("amount")
                note = request.form.get("note")
                location = request.form.get("location")
                date = request.form.get("date")

                db.execute("""
                        INSERT INTO expenses(id, amount, note, expense_location, expense_date, user_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (id, amount, note, location, date, user_id))           
                db.commit()

                flash("Changes saved!", "success")     
                return redirect(url_for("views.home"))
        else:      
            if request.method == "POST":
                # Get all variables from form
                amount = request.form.get("amount")
                note = request.form.get("note")
                location = request.form.get("location")
                date = request.form.get("date")



                # Insert values into database
                db.execute("""
                        INSERT INTO expenses(amount, note, expense_location, expense_date, user_id)
                        VALUES (?, ?, ?, ?, ?)
                        """, (amount, note, location, date, user_id))
                db.commit()
                flash("Expense added!", "success")
                return redirect(url_for("views.home"))
                
            else:
                return render_template("expense.html", data=None)
    else:
        return redirect(url_for("views.login"))
    
    
@views.route('/delete_expense/<int:id>', methods=["GET", "POST"])
def delete_expense(id=None):
    # If id is provided (if delete button is clicked)
    if id is not None:
        # Get data
        data = db.execute("SELECT * FROM expenses WHERE id = ?", (id, )).fetchone()
        # Insert data into bin
        db.execute("""
            INSERT INTO bin(id, amount, note, expense_location, expense_date, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, data["amount"], data["note"], data["expense_location"], data["expense_date"], data["user_id"]))
        # Delete data from expenses
        db.execute("DELETE FROM expenses WHERE id = ?", (id, ))
        db.commit()
        flash("Moved to bin", "success")
        return redirect(url_for("views.home"))
    # If no id
    else:
        return redirect(url_for("views.home"))



@views.route('/loan_to', methods=["GET", "POST"])
@views.route('/loan_to/edit/<int:id>', methods=["GET", "POST"])
def loan_to(id=None):
    if session["username"] is not None:
        # If id is parsed
        if id is not None:
            if request.method == "GET":
                    data = db.execute("SELECT * FROM loan_to WHERE id = ?", (id, ))

                    return render_template("loan_to.html", data=data)
            else:
                amount = request.form.get("amount")
                person = request.form.get("person")
                note = request.form.get("note")
                creation_date = request.form.get("creation_date")
                return_date = request.form.get("return_date")

                # Delete old entry
                db.execute("DELETE FROM loan_to WHERE id = ?", (id, ))
                # Insert new values
                db.execute("""
                    INSERT INTO loan_to (id, amount, person, note, creation_date, return_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                           """, (id, amount, person, note, creation_date, return_date))
                db.commit()
                flash("Entry changed!", "success")
                return redirect(url_for("views.home"))
        else:
            if request.method == "POST":
                user_id_row = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()
                user_id = user_id_row["id"]
                amount = request.form.get("amount")
                person = request.form.get("person")
                note = request.form.get("note")
                creation_date = request.form.get("creation_date")
                return_date = request.form.get("return_date")

                # TODO: Insert into database
                db.execute("""
                        INSERT INTO loan_to (amount, person, note, creation_date, return_date, user_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (amount, person, note, creation_date, return_date, user_id))
                db.commit()
                flash("Added!", "success")
                return redirect(url_for("views.home"))                
            else:
                return render_template("loan_to.html")
    else:
        return redirect(url_for("views.login"))
    

@views.route('/delete_loans_to/<int:id>', methods=["GET", "POST"])
def delete_loans_to(id=None):
    #TODO: Move to bin
    ...