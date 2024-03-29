from app.controller.auth.auth import password_generator
from flask import Flask,Blueprint
import traceback
from flask_apispec.annotations import doc
from datetime import date
from flask_restful import Resource,reqparse,fields
from ..controller import *
from flask_apispec import marshal_with,MethodResource,use_kwargs

from marshmallow import Schema, fields

# contra_response_schema = dict(
#     message=fields.String(default='')
# )


api_bp = Blueprint('api', __name__)

registration = reqparse.RequestParser()
registration.add_argument('name', type=str,required=True,help="Name is required")
registration.add_argument('phone', type=int,required=True,help="Phone is required")
registration.add_argument('email', type=str,required=True,help="Email ID is required")
registration.add_argument('password', type=str,required=True,help="Password is required")

loginArgs = reqparse.RequestParser()
loginArgs.add_argument('email', type=str,required=True)
loginArgs.add_argument('password', type=str,required=True)

masterinfoArgs =  reqparse.RequestParser()
masterinfoArgs.add_argument('master', type=str)

updateProfileArgs = reqparse.RequestParser()
updateProfileArgs.add_argument('name', type=str,required=True,help="Name is required")
updateProfileArgs.add_argument('phone', type=int,required=True,help="Phone is required")
updateProfileArgs.add_argument('email', type=str,required=True,help="Email ID is required")
updateProfileArgs.add_argument('old_email', type=str,required=True,help="Old Email ID is required")

changePasswordArgs = reqparse.RequestParser()
changePasswordArgs.add_argument('password', type=str)
changePasswordArgs.add_argument('old_password', type=str)
changePasswordArgs.add_argument('email', type=str)

germination_APIArgs = reqparse.RequestParser()
germination_APIArgs.add_argument("attemptName",type=str,required=True)
germination_APIArgs.add_argument("tags",type=str,required=True)
germination_APIArgs.add_argument("email",type=str,required=True)
germination_APIArgs.add_argument("location",type=str,required=True)

JadasAPIArgs = reqparse.RequestParser()
JadasAPIArgs.add_argument('meters',type=int,required=True)
JadasAPIArgs.add_argument('ID',type=int,required=True)

germination_detailsAPIargs = reqparse.RequestParser()
germination_detailsAPIargs.add_argument('germination_date',type=int,required=True)
germination_detailsAPIargs.add_argument('avg_germination_duration',type=int,required=True)
germination_detailsAPIargs.add_argument('average_time_of_true_leaves',type=int,required=True)
germination_detailsAPIargs.add_argument('average_sapling_height',type=int,required=True)
germination_detailsAPIargs.add_argument('hardening_cycle',type=int,required=True)
germination_detailsAPIargs.add_argument('sapling_transplant_date',type=int,required=True)

germination_weeklyAPIargs = reqparse.RequestParser()
germination_weeklyAPIargs.add_argument('Date',type=int,required=True)
germination_weeklyAPIargs.add_argument('Period',type=int,required=True)
germination_weeklyAPIargs.add_argument('Volume',type=int,required=True)
germination_weeklyAPIargs.add_argument('Time',type=int,required=True)
germination_weeklyAPIargs.add_argument('Doasge_EC',type=int,required=True)
germination_weeklyAPIargs.add_argument('Doasge_PH',type=int,required=True)
germination_weeklyAPIargs.add_argument('Pesticide',type=int,required=True)
germination_weeklyAPIargs.add_argument('Pesticide_Volume',type=int,required=True)

def initialize_routes(api):
    api.add_resource(contra,'/api/registration')
    api.add_resource(login,'/api/login')
    api.add_resource(updateProfile,'/api/updateProfile')
    api.add_resource(changePassword,'/api/changepassword')
    api.add_resource(resetPassword,'/api/resetpassword')
    api.add_resource(germination_API,'/api/germination')
    api.add_resource(germination_details,'/api/germination_details')
    api.add_resource(germination_weekly,'/api/germination_weekly')
    api.add_resource(Seeds_API,'/api/seeds')
    api.add_resource(JadasAPI,'/api/jadas')

resetpasswordArgs = reqparse.RequestParser()
resetpasswordArgs.add_argument('email',required=True,help="Email address Required.")


class JadasAPI(Resource):
    def get(self):
        data= mysql_query(''' 
        SELECT
	    *,
        Timestamp - LAG(Timestamp) OVER (ORDER BY Timestamp) 
                AS Timestamps_since_last_case
        FROM    Data
        ORDER BY Timestamp; ''')
        return jsonify({'Result: ':data})
    
    def post(self):
        args = JadasAPIArgs.parse_args()
        try:
            dt = mysql_query("select ID from Hits.Data order by DID desc limit 1;")
            print(dt)
            if str(dt[0]['ID']) != str(args['ID']):
                mysql_query('''
                    INSERT INTO `Hits`.`Data`
                    (`Meters`,`ID`)
                    VALUES
                    ({},{});'''.format(args['meters'],args['ID']))
        except pymysql.Error as e:
            return jsonify({"Error:": "could not close connection error pymysql %d: %s" %(e.args[0], e.args[1])})
        else:
            return {'Success':"Success"}

############### !# CONTRA
class contraResponseSchema(Schema):
    message = fields.Str(default='Success')

class contraRequestSchema(Schema):
    name = fields.String()
    phone = fields.Int()
    email = fields.String()
    password = fields.String()
    
class contra(MethodResource,Resource):
    @doc(description='User Registration', tags=['User Registration'])
    # @use_kwargs(contraRequestSchema,location=('json'))
    # @marshal_with(contraResponseSchema)
    def get(self):
        
        return {'message':"success"}

    @doc(description='User Registration', tags=['User Registration'] )
    @use_kwargs(contraRequestSchema,location=('json'),name='Body',required=True)
    @marshal_with(contraResponseSchema)
    def post(self):
        args = registration.parse_args()
        try:
            mysql_query(''' INSERT INTO `contra`.`auth`
                    (UTMID,
                    `Name`,
                    `Phone`,
                    `Emailid`,password)
                    VALUES
                    (2,'{}',{},'{}',md5('{}'));
                    '''.format(args['name'],args['phone'],args['email'],args['password']))
            
        except Exception as e:
           print("Oops!", e.__class__, "occurred.")
           return jsonify({'Error: ':str(e.__class__)})


############### !# LOGIN
class loginResponseSchema(Schema):
    message = fields.Str(default='Success')

class loginRequestSchema(Schema):
    email = fields.String()
    password = fields.String()
class login(MethodResource,Resource):
    @doc(description='Login', tags=['Login'] )
    @use_kwargs(loginRequestSchema,location=('json'),name='Body',required=True)
    @marshal_with(loginResponseSchema,code="404",description="Not Found")
    
    def post(self):
        args = loginArgs.parse_args()
        try:
            data = mysql_query(''' select Name,Phone,Emailid,Role from auth inner join user_type_master ON auth.UTMID=user_type_master.UTMID where auth.emailid='{}' and auth.password=md5('{}') limit 1; '''.format(args['email'],args['password']))
            print(data)
            if len(data) == 0:
                return {'Result':'User Does Not Exist'},404
            else:
                
                return {'Result':data[0]},200
        except Exception as e:
            return {'Failure':str(traceback.format_exc())}            

############### !# FORGOT PASSWORD
class forgotpasswordResponseSchema(Schema):
    status = fields.Str(default='Success')

class forgotpasswordRequestSchema(Schema):
    email = fields.String()
class resetPassword(MethodResource,Resource):
    @doc(description='Forgot Password', tags=['Forgot Password'] )
    @use_kwargs(forgotpasswordRequestSchema,location=('json'))
    @marshal_with(forgotpasswordResponseSchema)
    def post(self):
        args = resetpasswordArgs.parse_args()

        data = mysql_query("select count(*) as 'UE' from auth where emailid = '{}';".format(args['email']))
        print(data)
        if data[0]['UE'] == 1:
            otp = password_generator(6)
            deets = {'Emailid':args['email'],'Subject':'OTP','OTP':otp,'salutation':"Forgot Password"}
            send_mail(**deets)
            mysql_query("update auth SET password = md5('{}') where emailid ='{}';".format(otp,args['email']))
            return {'status':'Success'}
        else:
            return {'status':'No User'}

############### !# Update Profile #############
class updateProfileRequestSchema(Schema):
    name = fields.String()
    phone = fields.Int()
    email = fields.String()
    old_email = fields.String()

class updateProfileResponseSchema(Schema):
    status = fields.Str(default='Success')
class updateProfile(MethodResource,Resource):
    def post(self):
        args = updateProfileArgs.parse_args()

        data = mysql_query(''' UPDATE `contra`.`auth`
                                SET
                                `Name` = '{}',
                                `Phone` = {},
                                `Emailid` = '{}',
                            WHERE `Emailid` = '{}';
                                '''.format(args['name'], args['phone'], args['email'],args['old_email']))
        if mysql_query.row_count > 0:
            return {'status':'success'}
        else:
            return {'status':'No user Exist'}

############### !# CHANGE PASSWORD
class changePasswordRequestSchema(Schema):
    email = fields.String()
    password = fields.String()

class changePasswordResponseSchema(Schema):
    status = fields.Str(default='Success')
class changePassword(MethodResource,Resource):
    def post(self):
        args = changePasswordArgs.parse_args()

        data = mysql_query(''' UPDATE `contra`.`auth`
                                SET
                                `Password` = md5('{}')
                                WHERE `Emailid` = '{}';
                                '''.format(args['password'],args['email']))
        print(mysql_query.row_count)
        if mysql_query.row_count > 0:
            return {'status':'success'}
        else:
            return {'status':'No user Exist'}

class germination_API(Resource):
    def get(self):
        data = germination.ShowSystem()
        return jsonify({'Data':data})

    def post(self):
        args = germination_APIArgs.parse_args()
        germinationAPI = germination(email=args['email'])

        germinationAPI.AddSystem(attemptname=args['attemptName'],tags=args['tags'],location=args['location'])
        return jsonify({'Data':'success'})

class Seeds_API(Resource):
    def get(self):
        return jsonify({"Data":seeds.ShowSeeds()})

class germination_details(Resource):
    def post(self):
        # germination = germination_detailsAPIargs.parse_args()
        return jsonify({"Status":'Broken Link'})

class germination_weekly(Resource):
    def post(self):
        # germ = germination_weeklyAPIargs.parse_args()
        return jsonify({"Status":'AID Not provided'})