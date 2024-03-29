from flask import Flask, Blueprint, render_template, request, flash, session, redirect, url_for, g
from website import get_db_connection
from hashlib import pbkdf2_hmac
from functools import wraps

views = Blueprint('views', __name__)

# Connect to database
db = get_db_connection()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()
        if user_id is None:
            return redirect(url_for('views.login'))
        elif session["username"] is None:
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated_function
        
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
@login_required
def home():
    if request.method == "GET":
        if session["username"] is not None:
            user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()["id"]

            expenses_row = db.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id, )).fetchall()
            loans_to_row = db.execute("SELECT * FROM loan_to WHERE user_id = ?", (user_id, )).fetchall()
            # Get all expenses
            expenses = []
            expense_counter = 0
            for i in expenses_row:
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
@login_required
def expense(id=None):
    data = None
    user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()["id"]

    # if new expense is opened
    if id is None:
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
        
    # If expense is edited
    else:      
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

    
    
@views.route('/delete_expense/<int:id>', methods=["GET", "POST"])
def delete_expense(id=None):
    # If id is provided (if delete button is clicked)
    if id is not None:
        # Get data
        data = db.execute("SELECT * FROM expenses WHERE id = ?", (id, )).fetchone()
        # Insert data into bin
        db.execute("""
            INSERT INTO expense_bin(id, amount, note, expense_location, expense_date, user_id)
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
@login_required
def loan_to(id=None):
    user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()["id"]
    # If new loan_to is opened
    if id is None:
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
            return render_template("loan_to.html", data=None)
        
    # If loan_to is being edited
    else:
        if request.method == "GET":
                data = db.execute("SELECT * FROM loan_to WHERE id = ?", (id, )).fetchone()

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
                INSERT INTO loan_to (id, amount, person, note, creation_date, return_date, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (id, amount, person, note, creation_date, return_date, user_id))
            db.commit()
            flash("Changes saved!", "success")
            return redirect(url_for("views.home"))
    

@views.route('/delete_loan_to/<int:id>', methods=["GET", "POST"])
def delete_loans_to(id=None):
    if id is not None:
        #Fetch data
        data = db.execute("SELECT * FROM loan_to WHERE id = ?", (id, )).fetchone()

        # Move to bin
        db.execute("""INSERT INTO loan_to_bin (id, amount, person, note, creation_date, return_date, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["id"], data["amount"], data["person"], data["note"], data["creation_date"], data["return_date"], data["user_id"])
                )
        # Delete from view
        db.execute("DELETE FROM loan_to WHERE id = ?", (id, ))
        db.commit()
        flash("Moved to bin!", "success")
        return redirect(url_for('views.home'))
    else:
        return redirect(url_for("views.home"))

    
@views.route('/bin', methods=["GET", "POST"])
@views.route('/bin/restore/<string:item_type>/<int:id>', methods=["GET", "POST"])
@login_required
def bin(item_type=None, id=None):
    # If restore or delete button pressed
    if item_type and id is not None:
        if item_type == "expense":
            # Get data from bin
            data = db.execute("SELECT * FROM expense_bin WHERE id = ?", (id, )).fetchone()
            # Move data back to home
            db.execute("""INSERT INTO expenses (id, amount, note, expense_location, expense_date, user_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                       (data["id"], data["amount"], data["note"], data["expense_location"], data["expense_date"], data["user_id"]))
            # Delete data from bin
            db.execute("DELETE FROM expense_bin WHERE id = ?", (id, ))
            db.commit()

            return redirect(url_for("views.bin"))    
        elif item_type == "loan_to":
            # Get data from bin
            data = db.execute("SELECT * FROM loan_to_bin WHERE id = ?", (id, )).fetchone()
            # Move data back to home
            db.execute("""INSERT INTO loan_to (id, amount, person, note, creation_date, return_date, user_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (data["id"], data["amount"], data["person"], data["note"], data["creation_date"], data["return_date"], data["user_id"]))
            # Delete data from bin
            db.execute("DELETE FROM loan_to_bin WHERE id = ?", (id, ))
            db.commit()

            return redirect(url_for("views.bin"))
    # If bin is being viewed
    else:
        user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()["id"]
        expense_bin_row = db.execute("SELECT * FROM expense_bin WHERE user_id = ?", (user_id, )).fetchall()
        loan_to_row = db.execute("SELECT * FROM loan_to_bin WHERE user_id = ?", (user_id, )).fetchall()
        expense_data = []
        loan_to_data = []
        expense_counter = 0
        loan_to_counter = 0

        for _ in expense_bin_row:
            expense_data.append({
                    "id": expense_bin_row[expense_counter]["id"],
                    "amount": expense_bin_row[expense_counter]["amount"],
                    "note": expense_bin_row[expense_counter]["note"],
                    "expense_location": expense_bin_row[expense_counter]["expense_location"],
                    "expense_date": expense_bin_row[expense_counter]["expense_date"]
                })
            expense_counter += 1

        for _ in loan_to_row:
            loan_to_data.append({
                "id": loan_to_row[loan_to_counter]["id"],
                "amount": loan_to_row[loan_to_counter]["amount"],
                "person": loan_to_row[loan_to_counter]["person"],
                "note": loan_to_row[loan_to_counter]["note"],
                "creation_date": loan_to_row[loan_to_counter]["creation_date"],
                "return_date": loan_to_row[loan_to_counter]["return_date"]
            })
            loan_to_counter += 1

        return render_template("bin.html", expense_data=expense_data, loan_to_data=loan_to_data)
    

@views.route('/delete_from_bin/<string:item_type>/<int:id>')
def delete_from_bin(item_type=None, id=None):
    # If delete is pressed
    if item_type and id is not None:
        user_id = db.execute("SELECT id FROM users WHERE username = ?", (session["username"], )).fetchone()["id"]
        
        if item_type == "expense":
            db.execute("DELETE FROM expense_bin WHERE id = ? AND user_id = ?", (id, user_id))
            db.commit()
        elif item_type == "loan_to":
            db.execute("DELETE FROM loan_to_bin WHERE id = ? AND user_id = ?", (id, user_id))
            db.commit()

        return redirect(url_for("views.bin"))
    # If no id and item_type passed
    else:
        return redirect(url_for("views.home"))

