import sqlite3
from sqlite3 import Error
from datetime import datetime,timedelta
from flask import g,sessions
import secrets

# basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)
class Config(object):
    TESTING = False
    DEBUG = False
    FLASK_ENV='production'

    secret_key = secrets.token_hex(32)
    SECRET_KEY = secret_key
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)