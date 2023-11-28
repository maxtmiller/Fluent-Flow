import os
import requests
import secrets
import string
import re

from openai import OpenAI
from pathlib import Path

from cs50 import SQL
from functools import wraps
from flask import redirect, render_template, session, request, current_app, jsonify

import os.path
from sqlite3 import Error

from google.oauth2 import id_token
from google.auth.transport import requests

def login_required(f):
    """Decorate routes to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:

            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def before_first_request(f):
    """Decorate routes to execute before first request"""

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_app.config.get("BEFORE_FIRST_REQUEST"):

            return f(*args, **kwargs)

            current_app.config["BEFORE_FIRST_REQUEST"] = True

    return decorated_function


def run_sql(sql_file):
    """Runs SQL Commands from SQL File"""

    db = SQL("sqlite:///storage.db")

    try:
        with open('./static/'+sql_file, 'r') as file:
            sql_commands = file.read().split(';')
        for command in sql_commands:
            if command.strip():
                db.execute(command)
    except Error as e:
        print(e)


def check_for_sql(app):
    """Runs SQL files if they have not been run before"""

    db = SQL("sqlite:///storage.db")

    if not app.config.get("BEFORE_CHECK_EXECUTED"):

        run_sql('framework.sql')

        return

        app.config["BEFORE_CHECK_EXECUTED"] = True


def clear_session(app):
    """Clears Session and redirects to login page"""

    if not app.config.get("BEFORE_REQUEST_EXECUTED"):

        if request.endpoint != 'static' and request.endpoint != 'login':

            session.clear()

            return redirect("/login")

        app.config["BEFORE_REQUEST_EXECUTED"] = True


def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def valid_email(email):
    emailRegex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(emailRegex, email) is not None


def speech_to_text():

    return 1

# OPENAI_API_KEY = ""

# client = OpenAI(api_key=OPENAI_API_KEY)

# # audio_file= open("./static/audio_test.mp3", "rb")
# # transcript = client.audio.transcriptions.create(
# #     model="whisper-1", 
# #     file=audio_file,
# #     response_format="text"
# # )

# # return transcript

# completion = client.chat.completions.create(
# model="gpt-3.5-turbo",
# messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
# ]
# )

# print(completion.choices[0].message)

    
