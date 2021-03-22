import decimal,flask.json
from datetime import datetime,timedelta
from flask import g,sessions,json
import flask.json
import secrets


class Config(object):
    TESTING = True
    DEBUG = True
    FLASK_ENV='production'


    # SESSION_REFRESH_EACH_REQUEST = False
    # secret_key = secrets.token_hex(32)
    SECRET_KEY = '4834170ac147f19771b2c1aa90238683'
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)
    
    class MyJSONEncoder(flask.json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                # Convert decimal instances to strings.
                return str(obj)
            return super(MyJSONEncoder, self).default(obj)

