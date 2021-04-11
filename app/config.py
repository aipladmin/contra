import decimal,flask.json
from datetime import datetime,timedelta
from flask import g,sessions

class Config(object):
    TESTING = False
    DEBUG = False
    FLASK_ENV='production'


    # SESSION_REFRESH_EACH_REQUEST = False
    # secret_key = secrets.token_hex(32)
    SECRET_KEY = '11A8C8554CC8847E8335C922FC466'
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)
    
    class MyJSONEncoder(flask.json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                # Convert decimal instances to strings.
                return str(obj)
            return super(MyJSONEncoder, self).default(obj)

