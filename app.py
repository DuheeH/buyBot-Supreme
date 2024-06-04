import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect SQLite database
db = SQL("sqlite:///buybot.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        return redirect("/")
    return render_template("buy.html")


@app.route("/")
@login_required
def index():
    userid = session["user_id"]
    try:
        totalval = db.execute(
            "SELECT SUM(column_name)\
            FROM transactions\
            WHERE user_id=?",
            userid
        )
    except:
        return redirect("/buy")
    # Account total value
    return render_template(
        "index.html",
        totalval=totalval
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Invalid Username", 403)
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Invalid Password", 403)
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid Username and/or Password", 403)
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# registers the user
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if len(username) == 0:
            flash("Invalid Username")
            return redirect("/register")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username does not already exist
        if len(rows) != 0:
            flash("Invalid Username")
            return redirect("/register")

        # Ensure password exists
        if len(password) == 0:
            flash("Invalid Password")
            return redirect("/register")

        # Ensure password and confirmation match
        if password != confirmation:
            flash("Passwords Must Match")
            return redirect("/register")

        # Input username and password hash into user table in database
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)",
            username,
            generate_password_hash(password),
        )
        # redirects user to the homepage
        return redirect("/")
    # if GET method, renders the register.html
    return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    if request.method == "POST":
        profile = dict(request.form.items())
        #return render_template("test.html", profile=profile)
        try:
            if profile["sameAddress"]=="on":
                profile["addressB"] = profile["address"]
                profile["address2B"] = profile["address2"]
                profile["stateB"] = profile["state"]
                profile["zipB"] = profile["zip"]
                profile["countryB"] = profile["country"]
        except:
            profile["sameAddress"]='off'
        for key in profile:
            db.execute("UPDATE users SET ?=? WHERE id = ?", key, profile[key], user_id)
        profile_recent = db.execute("SELECT * FROM users WHERE id=?", user_id)
        profile_recent=profile_recent[0]
        #return render_template("test.html")
        return render_template("profile.html", profile_recent=profile_recent)
    profile_recent = db.execute("SELECT * FROM users WHERE id=?", user_id)
    profile_recent=profile_recent[0]
    #profile_test=profile_recent
    #return render_template("test.html", profile_test=profile_test)
    return render_template("profile.html", profile_recent=profile_recent)


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "POST":
        userid = session["user_id"]
        password = request.form.get("password")
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE id = ?", userid)
        # Checks previous password
        if len(password) == 0 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid Password", "error")
            return redirect("/changepass")

        # Checks new password
        if len(newpassword) == 0:
            flash("Must Provide New Password", "error")
            return redirect("/changepass")

        # Ensure password and confirmation match
        if newpassword != confirmation:
            flash("New Passwords Must Match", "error")
            return redirect("/changepass")

        # Checks new vs previous password
        if password == newpassword:
            flash("Provide New Password")
            return redirect("/changepass")

        # Update passwords
        db.execute(
            "UPDATE users SET hash=? WHERE id=?",
            generate_password_hash(newpassword),
            userid,
        )
        # redirects user to the homepage
        flash("Password Updated")
        return redirect("/")

    # if GET method, renders the changepass.html
    return render_template("changepass.html")