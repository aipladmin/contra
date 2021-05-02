from flask import Flask,Blueprint
from flask_mail import Mail
from flask_restful import Api
import decimal,flask.json
from .config import Config
from .controller.auth.api_bp import contra, forgotpasswordRequestSchema, initialize_routes, login, resetPassword
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=''
    )



    app.config.from_object(Config)
 
 
    

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
        auth,admin,api_bp
    )
    

    app.register_blueprint(auth.auth)
    app.register_blueprint(admin.admin)
    app.register_blueprint(api_bp.api_bp)
    api = Api(app)

    initialize_routes(api)

    app.register_blueprint(api_bp.api_bp)  
    
    return app
