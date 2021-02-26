import random
import string
import sqlite3
# import email
from flaskext.mysql import *
from functools import wraps
from flask_mail import Mail,Message
from flask import *

mysql = MySQL()

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'MiloniMadhav'
app.config['MYSQL_DATABASE_DB'] = 'contra'
app.config['MYSQL_DATABASE_HOST'] =  'contra.cjrbdmxkv84s.ap-south-1.rds.amazonaws.com'
mysql.init_app(app)

def mysql_query(sql):
    connection = mysql.connect()
    cursor = connection.cursor()
    if sql.strip().split(' ')[0].lower() == "select" :
        cursor.execute(sql)
        print(cursor._executed)
        
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        data = results
        cursor.close()
        connection.close()
        return data
    if sql.strip().split(' ')[0].lower() != "select" :
        print(sql)
        cursor.execute(sql)
        print(cursor._executed)
        mysql_query.last_row_id = cursor.lastrowid
        
        connection.commit()
        cursor.close()
        connection.close()
        return None


# DECORATORS
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session:
          return f(*args, **kwargs)
        else:
          return redirect(url_for('auth.login'))
    return wrap

def sql_query(sql, sqldt):
    # print("SQLDT:"+sqldt)
    try:
        print(sql, "        ", sqldt)
        if sqldt is not None:
            with sqlite3.connect("app.db") as con:
                cur = con.cursor()
                print(sql, "        ", sqldt)
                cur.execute(sql, sqldt)
                if sql.split(' ')[0].lower() == "select" :
                    rows = cur.fetchall()
                    flag =1
                else:
                    con.commit()
                    flag=0

        if sqldt is None:
            with sqlite3.connect("app.db") as con:
                cur = con.cursor()
                print(sql)
                cur.execute(sql)
                rows = cur.fetchall()
                flag=1
    except con.Error as e:
        print("Error: {}".format(e.args[0]))
    finally:
        con.close()
        
        if flag == 0:
            con.close()
            pass
        else:
            con.close()
            return rows

# MAIL DRIVER
def send_mail(**deets):
    mail = Mail()
        # with current_app.app_context():
    #     mail = Mail()
    #     mail.send(msg)
    # print(deets['otp'])
    msg = Message(deets['Subject'], sender = 'developer.websupp@gmail.com', recipients = [deets['Emailid'] ])
    # print(msg)
    msg.html = render_template('mail.html',emailid=deets['Emailid'],otp=deets['OTP'],salutation = deets['salutation'])
    mail.send(msg)
    return "mail"