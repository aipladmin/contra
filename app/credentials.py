from flaskext.mysql import MySQL
from flask import *

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'adminadmin'
app.config['MYSQL_DATABASE_DB'] = 'finrep'
app.config['MYSQL_DATABASE_HOST'] =  'aipldb.cttdwedcfzhs.ap-south-1.rds.amazonaws.com'