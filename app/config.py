import decimal,flask.json
from datetime import datetime,timedelta

class Config(object):
    TESTING = False
    DEBUG = False
    FLASK_ENV='production'


    # SESSION_REFRESH_EACH_REQUEST = False
    # secret_key = secrets.token_hex(32)
    SECRET_KEY = '11A8C8554CC8847E8335C922FC466'
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=30)
