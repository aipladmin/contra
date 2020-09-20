import sqlite3
from sqlite3 import Error
from datetime import datetime,timedelta
from flask import g,sessions


# basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)
class Config(object):
    TESTING = True
    DEBUG = True
    FLASK_ENV='production'

    SECRET_KEY = 'Sm9obiBTY2hyb20ga2lja3MgYXNz'
