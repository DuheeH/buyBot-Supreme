from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_binary
import time
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, usd, getProfile, randomWait

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
    user_id = session['user_id']
    if request.method == "POST":
        user_id = session["user_id"]
        urls = request.form.getlist('url')
        quantities = request.form.getlist('quantity')
        date_time = datetime.now()
        db.execute("""
            CREATE TABLE IF NOT EXISTS transactions
            (id INTEGER PRIMARY KEY,
            url TEXT,
            quantity INTEGER,
            price FLOAT,
            datetime DATETIME,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id))
        """)

        wd = webdriver.Chrome()
        profile = getProfile()
        profile_columns = ['firstName', 'lastName', 'email', 'address', 'address2', 'city', 'state', 'zip', 'phone', 'ccName', 'ccNumber', 'ccExpiration', 'ccSecurity']
        xpath_dict = {
            'addCart' : '//*[@id="product-root"]/div/div[2]/div[2]/form/div[2]/div/div[4]/div[2]/div[2]/div[3]/div[1]/input',
            'price' : '//*[@id="product-root"]/div/div[2]/div[2]/form/div[2]/div/div[4]/div[1]/div[2]',
            'checkout' : '//*[@id="product-root"]/div/div[1]/div/div/div/a[2]',
            'processPayment': '//*[@id="checkout-pay-button"]',
            'firstName': '//*[@id="TextField0"]',
            'lastName': '//*[@id="TextField1"]',
            'email': '//*[@id="email"]',
            'address': '//*[@id="shipping-address1"]',
            'address2': '//*[@id="TextField2"]',
            'city': '//*[@id="TextField3"]',
            'state': '//*[@id="Select1"]',
            'zip': '//*[@id="TextField4"]',
            'phone': '//*[@id="TextField5"]',
            'ccName': '//*[@id="name"]',
            'ccNumber': '//*[@id="number"]',
            'ccExpiration': '//*[@id="expiry"]',
            'ccSecurity': '//*[@id="verification_value"]'
        }
        prices = []
        for index, url in enumerate(urls):
            wait = WebDriverWait(wd, 10)
            wd.get(url)
            # Add items to cart X times 
            for _ in range(int(quantities[index])):
                wd.find_element(By.XPATH, xpath_dict['addCart']).click()
            # Add price to prices list
            prices.append(wd.find_element(By.XPATH, xpath_dict['price']).text)
            randomWait()
            # Go to checkout
            wd.find_element(By.XPATH, xpath_dict['checkout']).click()
            randomWait()
            # Fill in checkout info
            for column in profile_columns:
                value = str(profile[column])
                xpath = xpath_dict[column]
                element = WebDriverWait(wd, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))
                element.send_keys(value)
            # Process Payment
            input("enter to continue")
            return render_template('test.html')
            wd.find_element(By.XPATH, xpath_dict['processPayment']).click()
            wd.quit
        for index, url in enumerate(urls):
            quantity = float(quantities[index])
            db.execute("""
                INSERT INTO transactions
                (url, quantity, price, datetime, user_id)
                VALUES(?,?,?,?,?)
            """, url, quantity, prices[index], date_time, user_id)
        flash("Purchase Successful!")
        return redirect("/")
    try:
        rows=db.execute("""
            SELECT * FROM profiles
            WHERE id = ?
            """, user_id)
        rows = rows[0]
        return render_template("buy.html")
    except:
        flash("| Profile Required Prior to Purchase |")
        return redirect("/profile")

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    totalVal = db.execute("""
            SELECT SUM(price*quantity) AS totalVal
            FROM transactions
            WHERE user_id=?
        """, user_id
        )
    if totalVal[0]['totalVal'] is None:
        flash("| No Transactions | ")
        return redirect("/buy")
    # Account total value
    transaction_rows = db.execute("""
            SELECT url,price,quantity,(price*quantity),datetime
            FROM transactions
            WHERE user_id = ?""",
            user_id
        )
    return render_template(
        "index.html",
        totalVal=totalVal,
        transaction_rows=transaction_rows
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
        return redirect("/profile")

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
        test = db.execute("""SELECT * FROM profiles WHERE user_id=?""",user_id)
        if not test:
            db.execute("""
                INSERT INTO profiles (user_id)
                VALUES (?)
                """, user_id)
        for key,value in profile.items():
            db.execute("""
                UPDATE profiles
                SET ?=?
                WHERE user_id=?
                """, key, value, user_id)
        profile_recent = getProfile()
        flash("Profile Updated")
        return render_template("profile.html", profile_recent=profile_recent)
    db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        firstName TEXT,
        lastName TEXT,
        email TEXT,
        address TEXT,
        address2 TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        phone TEXT,
        ccName TEXT,
        ccNumber TEXT,
        ccExpiration TEXT,
        ccSecurity TEXT,
        sameAddress TEXT DEFAULT 'on',
        FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
    profile_recent = getProfile()
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