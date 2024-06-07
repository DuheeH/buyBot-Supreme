from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps
import random
import time

# Connect SQLite database
db = SQL("sqlite:///buybot.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def getTable(table):
    """Retrieves up-to-date profile info"""
    user_id = session["user_id"]
    try:
        table_recent = db.execute("SELECT * FROM ? WHERE user_id=? ORDER BY datetime DESC", table, user_id)
    except:
        table_recent = db.execute("SELECT * FROM ? WHERE user_id=?", table, user_id)
    if len(table_recent) <= 1:
        return table_recent[0]
    return table_recent

def randomWait():
    randon_wait = random.randrange(1,5)
    time.sleep(randon_wait)

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code