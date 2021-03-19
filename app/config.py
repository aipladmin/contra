import sqlite3
from sqlite3 import Error
from datetime import datetime,timedelta
from flask import g,sessions
import secrets

# basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)
class Config(object):
    TESTING = True
    DEBUG = True
    FLASK_ENV='production'

    # SESSION_REFRESH_EACH_REQUEST = False
    # secret_key = secrets.token_hex(32)
    SECRET_KEY = '4834170ac147f19771b2c1aa90238683'
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)
