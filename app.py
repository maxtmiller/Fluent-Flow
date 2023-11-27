import os.path
import requests
import sqlite3

from cs50 import SQL
from sqlite3 import Error
from flask import Flask, flash, redirect, render_template, session, request, current_app, jsonify, url_for
from flask_session import Session

from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, before_first_request, run_sql, check_for_sql, clear_session, generate_password, valid_email

from google.oauth2 import id_token
from google.auth.transport import requests


# From CS50 Module - (Configure application)
app = Flask(__name__)


# From CS50 Module - (Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# From CS50 Module - (Configure CS50 Library to use SQLite database)
db = SQL("sqlite:///storage.db")


# From CS50 Module
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.before_request
@before_first_request
def before_request():
    """Clear Session"""

    # Checks if college list is populated
    check_for_sql(app)

    # Calls function to redirect to login page only on app start
    clear_session(app)

    return


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Clear any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Variable for storing error message
        error = None

        # Ensure username was submitted
        if not request.form.get("user"):
            error = "Must provide email or username!"
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password!"
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", request.form.get("user"), request.form.get("user"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Invalid username and/or password!"
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        print("success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        new_email = request.form.get("email")
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        new_confirmation = request.form.get("confirmation")

        existing_email = db.execute("SELECT * FROM users WHERE email = ?", new_email)
        existing_username = db.execute("SELECT * FROM users WHERE username = ?", new_username)

        # Variable for storing error message
        error = None

        # Ensure email was submitted
        if not new_email:
            error = "Must provide email!"
            return render_template("register.html", error=error)
        
        # Ensure email is not already registered to an account
        elif len(existing_email) != 0:
            error = "Account already exists with specified email!"
            return render_template("register.html", error=error)
        
        elif valid_email(new_email) == False:
            error = "Invalid email provided!"
            return render_template("register.html", error=error)

        # Ensure username is provided
        elif not new_username:
            error = "Must provide username!"
            return render_template("register.html", error=error)

        # Ensure username is unique
        elif len(existing_username) != 0:
            error = "Username not available!"
            return render_template("register.html", error=error)

        # Ensure password was submitted
        elif not new_password:
            error = "Missing password!"
            return render_template("register.html", error=error)

        # Ensure passwords match
        elif new_password != new_confirmation:
            error = "Passwords don't match!"
            return render_template("register.html", error=error)

        # Ensure password is between 4 and 15 characters
        elif len(new_password) < 4 or len(new_password) > 15:
            error = "Password must be between 4 and 15 characters long!"
            return render_template("register.html", error=error)

        # Hashes password when before inserting into users table
        hash = generate_password_hash(new_password, method='pbkdf2', salt_length=16)

        db.execute("INSERT INTO USERS (email, username, hash, auto_generated) VALUES(?, ?, ?, ?)", new_email, new_username, hash, False)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]

        flash("Registered!")
        return redirect("/")

    else:

        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/")
@login_required
def home():
    """Home Page"""

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?;", user_id)[0]

    return render_template("home.html", user=user)


@app.route("/menu")
@login_required
def menu():
    """Sample Page"""

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?;", user_id)[0]

    return render_template("menu.html", user=user)


@app.route("/about")
@login_required
def about():
    """About Page"""

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?;", user_id)[0]

    return render_template("about.html",  user=user)


@app.route("/settings", methods=["GET", "POST"] )
@login_required
def settings():
    """Settings Page"""

    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?;", user_id)[0]

    generated = user['auto_generated']

    print("generated", generated)

    if request.method == "POST":

        # confirmation = request.json['displayProperty']
        # print("confirmation python: ", confirmation)

        error = None
        success = None

        new_username = request.form.get("username")
        new_email = request.form.get("email")
       
        if generated:
            set_password = request.form.get("set-password")
        else:
            new_password = request.form.get("new-password")
            current_password = request.form.get("current-password")

        print(user['id'], new_username, new_email)

        existing_usernames = db.execute("SELECT * FROM users WHERE username = ? AND NOT id = ?", new_username, user['id'])
        existing_emails = db.execute("SELECT * FROM users WHERE email = ? AND NOT id = ?", new_email, user['id'])

        hash = db.execute("SELECT hash FROM users WHERE id = ?", user['id'])[0]['hash']

        if not new_username or not new_email:
            error = "Must fill all fields!"
            return render_template("settings.html",  user=user, error=error)
        
        elif len(existing_usernames) != 0:
            error = "Username already taken!"
            return render_template("settings.html",  user=user, error=error)

        elif len(existing_emails) != 0:
            error = "Account already exists for specified email!"
            return render_template("settings.html",  user=user, error=error)

        elif valid_email(new_email) == False:
            error = "Invalid email provided!"
            return render_template("settings.html",  user=user, error=error)

        elif generated:

            if len(set_password) < 4 or len(set_password) > 15:
                error = "Password must be between 4 and 15 characters long!"
                return render_template("settings.html",  user=user, error=error)

        elif not generated:

            if not check_password_hash(hash, current_password):
                error = "Current password incorrect!"
                return render_template("settings.html",  user=user, error=error)

            elif len(new_password) < 4 or len(new_password) > 15:
                error = "Password must be between 4 and 15 characters long!"
                return render_template("settings.html",  user=user, error=error)

            elif new_username == user['username'] and new_email == user['email'] and check_password_hash(hash, new_password):
                error = "Account Details have not changed!"
                print("all")
                return render_template("settings.html",  user=user, error=error)

        if new_username == user['username'] and new_email != user['email']:
            db.execute("UPDATE users SET email = ? WHERE id = ?;", new_email, user['id'])
            success = "Email succesfully updated!"
            return render_template("settings.html",  user=user, success=success)
        
        elif new_username != user['username'] and new_email == user['email']:
            db.execute("UPDATE users SET username = ? WHERE id = ?;", new_username, user['id'])
            success = "Username succesfully updated!"
            return render_template("settings.html",  user=user, success=success)

        elif generated:
            hash = generate_password_hash(set_password, method='pbkdf2', salt_length=16)
            db.execute("UPDATE users SET hash = ?;", hash)
            db.execute("UPDATE users SET auto_generated = ?;", False)
            success = "Password succesfully set!"
            return render_template("settings.html",  user=user, success=success)

        elif not generated:

            if new_username != current_password and check_password_hash(hash, current_password):
                hash = generate_password_hash(new_password, method='pbkdf2', salt_length=16)
                db.execute("UPDATE users SET hash = ?;", hash)
                success = "Password succesfully updated!"
                return render_template("settings.html",  user=user, success=success)

        return render_template("settings.html",  user=user)

    return render_template("settings.html",  user=user, generated=generated)


@app.route('/google-signin', methods=['POST'])
def google_signin():

    YOUR_CLIENT_ID = '434447398181-dte88c2s0pdun9rl3h5k942v6tgtj7ue.apps.googleusercontent.com'

    id_token_received = request.form['id_token']

    try:
        # Verify the id_token
        idinfo = id_token.verify_oauth2_token(id_token_received, requests.Request(), YOUR_CLIENT_ID)

        # Extract user information
        user_id = idinfo['sub']
        user_name = idinfo['name']
        user_email = idinfo['email']

        # Search for users with email
        email_count = db.execute("SELECT COUNT(email) FROM users WHERE email = ?;", user_email)
        email_count = email_count[0]["COUNT(email)"]

        if email_count != 1:

            email = user_email
            username = user_name
            password = generate_password(12)
            hash = generate_password_hash(password, method='pbkdf2', salt_length=16)

            db.execute("INSERT INTO USERS (email, username, hash, auto_generated) VALUES(?, ?, ?, ?);", email, username, hash, True)

            rows = db.execute("SELECT * FROM users WHERE email = ?", email)

            print("rows - ", rows)

            session["user_id"] = rows[0]["id"]

        else:

            email = user_email

            rows = db.execute("SELECT * FROM users WHERE email = ?;", email)

            session["user_id"] = rows[0]["id"]

        return jsonify(success=True)

    except ValueError:
        print('Invalid token')
        return jsonify(success=False, error='Invalid token')
    

@app.route('/get_styling', methods=['POST'])
def get_styling():

    confirmation = request.json['displayProperty']
    print("confirmation python: ", confirmation)

    return jsonify(confirmation)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="3000", debug=True)
