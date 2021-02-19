from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for, abort, jsonify
# from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.exceptions import HTTPException
import sqlite3
import random,json
import string
from ..sqlq import *

auth = Blueprint('auth',
                __name__,
                template_folder="auth_templates",
                static_folder="auth_static",
                url_prefix='/')

def password_generator(length):
    letters = string.digits
    rpassword = ''.join(random.choice(letters) for i in range(length))
    return rpassword

@auth.app_errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@auth.route('/')
def login():
    # cur = g.db.cursor()
    # cur.execute("select * from auth")
    # rows = cur.fetchall()
    # print(rows)
    return render_template('login.html')

@auth.route('/loginscr',methods=['POST'])
def loginscr():
    email = request.form['emailid']
    password = request.form['password']
    data = mysql_query("select count(*) as 'user_exists',user_type_master.Role,auth.AID from auth inner join user_type_master ON auth.UTMID=user_type_master.UTMID where Emailid='{}' and Password=md5('{}');".format(email,password))
    print(data[0]['user_exists'])
    
    if data[0]['user_exists'] == 0:
        return 'unauthorized user'
    elif data[0]['user_exists'] == 1:
        otp = password_generator(6)
        session['email'] = email
        session['role'] = data[0]['Role']
        # session['all'] = {'email':email,'role':data[0]['Role'],'AID':data[0]['AID']}
        
        mysql_query(''' UPDATE `contra`.`auth`
                        SET
                        `OTP` = {}                      
                        WHERE Emailid='{}';
                        '''.format(otp,session['email']))

        deets = {'Emailid':session['email'],'Subject':'OTP','OTP':otp,'salutation':"salutation"}
        
        send_mail(**deets)
      
        return redirect(url_for('auth.otp'))
        # return redirect(url_for('auth.index'))
    return "loginscr"

@auth.route('/OTP',methods=['GET','POST'])
def otp():
    if request.method == 'POST':
        dt = mysql_query("select * from auth where OTP={};".format(request.form['otp']))
        if len(dt) == 0:
            return "Invalid OTP."
        else:
            AID= dt[0]['AID']
            mysql_query("INSERT into Auth_Logs(AID,Method) values({},'Login')".format(AID))
            session.permanent = True
            return redirect(url_for('auth.index'))

    return render_template('otp.html')

@auth.route('/index')
@login_required
def index():
    return render_template('index.html')

# LOGOUT CODE
@auth.route('/logout')
@login_required
def logout():
    AID = mysql_query("select AID from auth where Emailid='{}';".format(session['email']))
    mysql_query("insert into Auth_Logs(AID,Method) values({},'Logout')".format(AID[0]['AID']))
    session.pop('email', None)
    session.pop('role', None)
    
    return redirect(url_for('auth.login'))



