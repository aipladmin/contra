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
    letters = string.ascii_lowercase
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
        session['email'] = email
        session['role'] = data[0]['Role']
        session['all'] = {'email':email,'role':data[0]['Role'],'AID':data[0]['AID']}
        return redirect(url_for('auth.index'))
    return "loginscr"

@auth.route('/index')
def index():
    return render_template('index.html')

# LOGOUT CODE
@auth.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))


@auth.route('/index')
@login_required
def index_template():
    return render_template('index.html')


