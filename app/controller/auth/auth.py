from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for
# from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from functools import wraps


import sqlite3
import random
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


# GLOBAL Before Request and after request
# DO NOT TOUCH
# @auth.before_app_request
# def dbconn():
# 	conn = sqlite3.connect('app.db')
# 	g.db = conn


# @auth.after_app_request
# def closeconn(response):
# 	if g.db is not None:
# 		print('closing connection')
# 		g.db.close()
# 	return response

# DECORATORS
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session and 'role' in session:
            return f(*args, **kwargs)
        else:
            # flash('You need to login first')
            return redirect(url_for('auth.login'))
    return wrap


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

@auth.route('/test/')
def test():
    # admin = tuple()
    # data = new_mysql_query(sql="update user_type_master SET Role='{}' where UTMID={} ".format('admin',1))

    
    
    return "<h5>Test:</h5> <p>" + str(data) + "</p><p>"+str(data)+"</p>"




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


@auth.route('/prac')
@login_required
def prac():
    return render_template('prac.htm.j2')
