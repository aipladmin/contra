import os
import sqlite3
from flask import Flask
from flask_mail import Mail
from flaskext.mysql import MySQL

from .config import Config

def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=''
    )
    # app.config.from_pyfile('config.py')

    app.config.from_object(Config)

    

    # mysql = MySQL()
    # app.config['MYSQL_DATABASE_USER'] = 'admin'
    # app.config['MYSQL_DATABASE_PASSWORD'] = 'adminadmin'
    # app.config['MYSQL_DATABASE_DB'] = 'finrep'
    # app.config['MYSQL_DATABASE_HOST'] =  'aipldb.cttdwedcfzhs.ap-south-1.rds.amazonaws.com'
    # mysql.init_app(app)

    mail = Mail()
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT']=465
    app.config['MAIL_USE_SSL']=True
    app.config['MAIL_USERNAME'] = 'developer.websupp@gmail.com'
    app.config['MAIL_PASSWORD'] = 'jvlfatxjxjigmryg'
    app.config['MAIL_DEFAULT_SENDER'] = 'developer.websupp@gmail.com'
    app.config['MAIL_USE_TLS'] = False 
    mail.init_app(app)



    from app.controller.auth import (
        auth,admin,api
    )
    

    app.register_blueprint(auth.auth)
    app.register_blueprint(admin.admin)
    app.register_blueprint(api.api)
    
    
    return app
