import sqlite3
from flaskext.mysql import *
from functools import wraps
from datetime import datetime
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
        print(sql)
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
        mysql_query.row_count = cursor.rowcount
        connection.commit()
        cursor.close()
        connection.close()
        return None


# DECORATORS
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' in session and 'role' in session:
            return f(*args, **kwargs)
        return redirect(url_for('auth.login'))

    return wrap

# MAIL DRIVER
def send_mail(**deets):
    mail = Mail()
    
    msg = Message(deets['Subject'], sender = 'developer.websupp@gmail.com', recipients = [deets['Emailid'] ])
    msg.html = render_template('mail.html',emailid=deets['Emailid'],otp=deets['OTP'],salutation = deets['salutation'])
    mail.send(msg)
    return "mail"
class getUID():
    def __init__(self,email):
        self.email = email
    
    def getAID(self):
        AID = mysql_query("select AID from auth where Emailid='{}';".format(self.email))
        return AID
    
    def getGID(self):
        email=self.email
        GID = mysql_query("select GID from germination inner join auth ON auth.AID = germination.AID where auth.Emailid='{}';".format(email))
        return GID
class germination(getUID):
    def __init__(self,email):
        self.email=email
        getUID.__init__(self,email)
    
    @staticmethod
    def ShowSystem():
        data=mysql_query("select GemCode,Attempt_Name,Location,Tags from germination;")
        return data

    def AddSystem(self,attemptname,location,tags):
        gemcode = self.email[0:3].capitalize()+attemptname[0:3].capitalize()+datetime.now().strftime("/%d%m%y/%H/%M/%S")
        AID = self.getAID()
        AID=AID[0]['AID']
        print(AID)
        mysql_query('''INSERT INTO `contra`.`germination`
                            (AID,`Attempt_Name`,
                            `Location`,Tags,GemCode)
                            VALUES
                            ({},'{}','{}','{}','{}');'''.format(AID,attemptname,location,tags,gemcode))
        return "DI"

class seeds():
    @staticmethod
    def ShowSeeds():
        data = mysql_query("select * from seeds_master")
        return data