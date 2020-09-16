from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for
# from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from functools import wraps


import sqlite3
import random
import string
from .sqlq import *

bp = Blueprint('auth', __name__)


def password_generator(length):
    letters = string.ascii_lowercase
    rpassword = ''.join(random.choice(letters) for i in range(length))
    return rpassword


# GLOBAL Before Request and after request
# DO NOT TOUCH
# @bp.before_app_request
# def dbconn():
# 	conn = sqlite3.connect('app.db')
# 	g.db = conn


# @bp.after_app_request
# def closeconn(response):
# 	if g.db is not None:
# 		print('closing connection')
# 		g.db.close()
# 	return response

# DECORATORS
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        else:
            # flash('You need to login first')
            return redirect(url_for('auth.login'))
    return wrap


@bp.route('/')
def login():
    # cur = g.db.cursor()
    # cur.execute("select * from auth")
    # rows = cur.fetchall()
    # print(rows)
    return render_template('login.htm.j2')


@bp.route('/test/')
def test():
    tst = madhav()

    data = sql_query(sql="select * from auth", sqldt=None)
    dataa = sql_query(
        sql="INSERT OR REPLACE INTO auth (Emailid,Otp) VALUES (?,?) ",
        sqldt=('madhav.parik@gmail.com', 'tyhuui'))
    return "<h5>Test:</h5> <p>" + str(tst) + "</p><p>"+str(data)+"</p>"


@bp.route('/otp', methods=['POST'])
def loginotp():
    if request.method == 'POST':
        if 'login' in request.form:
            email = request.form['email']
            otp = password_generator(6)
            print(otp)
            sql_query(
                sql="INSERT or REPLACE INTO auth(Emailid, Otp) VALUES(?, ?) ",
                sqldt=(email, otp))

            session['email'] = email
            return render_template('loginotp.htm.j2')
        if 'otp_verification' in request.form:
            otp = request.form['password']
            rows = sql_query(
                sql="Select count(*) from auth where Emailid =? and otp =? and Activation='Activated' ",
                sqldt=(session['email'], otp))

            print("ROWS                 " + str(rows))
            if len(rows) == 1:
                return redirect(url_for('auth.index_template'))
            elif len(rows) == 0:
                return "rows 0"
            return 'loginotp'
    return 'loginotp'

# LOGOUT CODE


@bp.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    return redirect(url_for('auth.login'))


@bp.route('/index')
@login_required
def index_template():
    return render_template('index.html')


@bp.route('/prac')
@login_required
def prac():
    return render_template('prac.htm.j2')
