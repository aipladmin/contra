import sqlite3
from sqlite3 import Error
from datetime import datetime,timedelta
from flask import g,sessions


# basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)
class Config(object):
    # ...
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    TESTING = True
    DEBUG = True
    dev='development'
    FLASK_ENV=dev
    SECRET_KEY = 'Sm9obiBTY2hyb20ga2lja3MgYXNz'
    # permanent_session_lifetime = timedelta(seconds=5)

    # conn = sqlite3.connect('app.db')
    # print ("Opened database successfully")

    conn = sqlite3.connect('app.db')
    print("Opened database successfully")

    # conn.execute('Drop Table if exists app.auth')

    conn.execute
    (
        '''CREATE TABLE IF NOT EXISTS auth 
            (AID INTEGER PRIMARY KEY AUTOINCREMENT ,
            Emailid TEXT ,
            Otp TEXT,
            Role TEXT Default "User",
            Activation TEXT Default "Activated",
            CONSTRAINT email_unique UNIQUE (Emailid))'''
        )
    print("Table created successfully")
    conn.close()
