import csv
import datetime
import pytz
import requests
import urllib
import uuid

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

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

def getProfile():
    """Retrieves up-to-date profile info"""
    user_id = session["user_id"]
    profile_recent = db.execute("SELECT * FROM users WHERE id=?", user_id)
    profile_recent=profile_recent[0]
    return profile_recent
