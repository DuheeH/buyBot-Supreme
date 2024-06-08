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

def getTable(table):
    """Retrieves up-to-date profile info"""
    user_id = session["user_id"]
    try:
        table_recent = db.execute("SELECT * FROM ? WHERE user_id=? ORDER BY datetime DESC", table, user_id)
    except:
        table_recent = db.execute("SELECT * FROM ? WHERE user_id=?", table, user_id)
    if len(table_recent) <= 1:
        try:
            return table_recent[0]
        except:
            return []
    return table_recent

def randomWait():
    randon_wait = random.randrange(1,5)
    time.sleep(randon_wait)