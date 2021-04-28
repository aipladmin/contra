from flask import Flask,Blueprint,request

from datetime import date
from flask_restful import Resource,reqparse
from ..controller import *


api_bp = Blueprint('api', __name__)

Contra1args = reqparse.RequestParser()
Contra1args.add_argument('name', type=str,required=True,help="Name cannot be blank!")
Contra1args.add_argument('phone', type=str,required=True,help="Phone cannot be blank!")
Contra1args.add_argument('email', type=str,required=True,help="Email cannot be blank!")


def initialize_routes(api):
    api.add_resource(contra,'/contra')
    api.add_resource(contraEP2,'/contraEP2')


class contra(Resource):
    def get(self):
        
        return {'status':"success"}
    
    def post(self):
        args = Contra1args.parse_args()
        return {'task':args}


class contraEP2(Resource):
    def get(self):
        return {'task': 'Contra Endpoint:2 '}
