from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for
import secrets
from ..sqlq import *

admin = Blueprint('admin',
                __name__,
                template_folder="auth_templates",
                static_folder="auth_static",
                url_prefix='/admin')

@admin.route('/')
def index():
    return 'index'

@admin.route('/boards')
def boards():
    
    arduinoID = secrets.token_hex(32)
    sensor_data = mysql_query('select SID,sensor_name from sensor_master;')
    boards = mysql_query("select distinct(boards.BID) as 'identifier',boards.Name,boards.UBID from boards inner join module on module.BID = boards.BID order by boards.BID ASC;")
    sensors = mysql_query('select boards.BID,module.mid,sensor_master.Sensor_Name,sensor_master.Type from module inner join boards on module.BID=boards.BID inner join sensor_master on sensor_master.SID = module.SID order by boards.BID ASC;')
    return render_template('admin/boards.html',arduinoID = arduinoID,sensor_data=sensor_data,boards=boards,sensors=sensors)

@admin.route('/boardscr',methods=['GET','POST'])
def boardscr():
    if request.method == "POST":
        if "insert" in request.form:
            sensors = request.form.getlist('sensors')
            print(request.form['UBID'])

            AID = mysql_query("select AID from auth where Emailid='{}';".format(session['email']))
            AID = AID[0]['AID']
            mysql_query("insert into boards(AID,UBID,Name) values({},'{}','{}');".format(AID,request.form['UBID'],request.form['name'] ))
            print(request.form['UBID'])
            BID = mysql_query("Select BID from boards where UBID='{}';".format(request.form['UBID'] ))
            BID = BID[0]['BID']
            for x in sensors:
                mysql_query("insert into module(BID,SID) values({},{}); ".format(BID,x))

            return str(BID)
    
    return "data"

@admin.route('/sensors',methods=['GET','POST'])
def sensors():
    if request.method == 'POST':
        if 'insert_sensor' in request.form:
            sensorname = request.form['name']
            sensortype = request.form['sensortype']
            mysql_query("insert into sensor_master(sensor_name,type) values('{}','{}')".format(sensorname,sensortype))
            return redirect(url_for('admin.sensors'))
        if 'update' in request.form:
            mysql_query(" update sensor_master SET sensor_name='{}',type='{}' where SID={};".format(request.form['sensorname'],request.form['sensortype'],request.form['update']))
            return redirect(url_for('admin.sensors'))
        if 'delete' in request.form:
            mysql_query(" delete from sensor_master where SID={};".format(request.form['delete']))
            return redirect(url_for('admin.sensors'))
        return "POST"
    data = mysql_query("select * from sensor_master")
    return render_template('admin/sensors.html',data=data)