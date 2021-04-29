from flask import Flask,Blueprint,request
import traceback
from datetime import date
from flask_restful import Resource,reqparse
from ..controller import *


api_bp = Blueprint('api', __name__)

Contra1args = reqparse.RequestParser()
Contra1args.add_argument('name', type=str)
Contra1args.add_argument('phone', type=int)
Contra1args.add_argument('email', type=str)
Contra1args.add_argument('password', type=str)



def initialize_routes(api):
    api.add_resource(contra,'/contra')
    api.add_resource(contraEP2,'/contraEP2')


class contra(Resource):
    def get(self):
        
        return {'status':"success"}
    
    def post(self):
        args = Contra1args.parse_args()
        try:
            mysql_query(''' INSERT INTO `contra`.`auth`
                    (UTMID,
                    `Name`,
                    `Phone`,
                    `Emailid`,password)
                    VALUES
                    (1,'{}',{},'{}',md5('{}'));
                    '''.format(args['name'],args['phone'],args['email'],args['password']))
            return {'Success':'Record Inserted'}
        except Exception as e:
            return {'Failure':str(traceback.format_exc())}            
        


class contraEP2(Resource):
    def get(self):
        return {'task': 'Contra Endpoint:2 '}
