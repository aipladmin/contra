from flask import Flask, render_template, Blueprint, request, session, redirect, url_for, abort, jsonify,flash
import secrets,json
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from ..sqlq import *

admin = Blueprint('admin',
                __name__,
                template_folder="auth_templates",
                static_folder="auth_static",
                url_prefix='/admin')

@admin.app_errorhandler(HTTPException)
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

@admin.route('/')
def index():
    return 'index'

@admin.route('/boards')
def boards():
    api_endpoint =request.host_url
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
            return redirect(url_for('admin.boards'))
        if "delete_boards" in request.form:
            UBID = request.form['UBID']
            mysql_query("delete module,boards from boards inner join module on boards.BID = module.BID where boards.UBID='{}';".format(UBID))
            return redirect(url_for('admin.boards'))

        if "update_boards" in request.form:
            mysql_query("update boards SET Name='{}' where UBID='{}';".format(request.form['name'],request.form['UBID'] ))
            return redirect(url_for('admin.boards'))
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

@admin.route('/germination')
def germination():
    return render_template('admin/germination.html')

@admin.route('/germination_scr',methods=['POST'])
def germination_scr():
    if request.method == "POST":
            try:
                total = int(request.form['soakedseeds'])+int(request.form['unsoakedseeds'])
                mysql_query('''INSERT INTO `contra`.`germination`
                            (`Attempt_Name`,
                            `Location`,
                            `Plant_Name`,
                            `Cec_Value`,
                            `Water_Ph`,
                            `Water_TDS`,
                            `Sowing_Date`,
                            `Grow_Medium`,
                            `Light_Source`,
                            `Seed_Company`,
                            `Seed_Variety`,
                            `Soaked_Seeds`,
                            `Unsoaked_Seeds`,
                            `Total`,
                            `Total_Plants`)
                            VALUES
                            ('{}','{}','{}',{},{},{},'{}','{}','{}','{}','{}',{},{},{},{});'''
                            .format(request.form['attemptname'],request.form['location'],request.form['plantname'],
                            request.form['Cocopeatecvalue'],request.form['waterph'],request.form['watertds'],request.form['sowingdate'],
                            request.form['growmedium'],request.form['lightsource'],request.form['seedcompany'],request.form['svariety'],
                            request.form['soakedseeds'],request.form['unsoakedseeds'],total,request.form['totalplants']))
                flash("Record(s) Inserted","success")
            except Exception as e:
                flash("Error: "+str(e),"failure")

            return redirect(url_for('admin.germination'))
            

    return "germination_scr"

@admin.route('/germinationweekly')
def germinationweekly():
    data = mysql_query("select *,date(convert_tz(now(),'+00:00','+05:30')) as 'Curdate' from germination;")
    return render_template('admin/germinationlist.html',data=data)

@admin.route('/germinationweekly_scr',methods=['POST'])
def germinationweekly_scr():
    if request.method == "POST":
        if 'weekly' in request.form:
            try:
                mysql_query("insert into germination_weekly(GID,Date,Period,Time,Volume,Dosage_EC,Dosage_PH,Pesticide,Pesticide_Volume) values({},'{}','{}','{}',{},{},{},'{}',{});"
                .format(request.form['attempt_id'],request.form['date'],request.form['period_of_time'],request.form['time'],request.form['volume'],request.
                form['dosage_ec'],request.form['dosage_ph'],request.form['pesticide'],request.form['pesticide_volume'] ) ) 
                flash("Record Inserted","success")
            except Exception as e:
                flash("Weekly: "+str(e),"error")
            return redirect(url_for('admin.germinationweekly'))
        if 'germination_desc' in request.form:
            try:
                mysql_query('''INSERT INTO `contra`.`germination_detail`
                        (`GID`,
                        `Germination_Date`,
                        `Average_Germination_Duration`,
                        `Average_Time_of_True_Leaves`,
                        `Average_Sapling_Height`,
                        `Hardening_Cycle`,
                        `Hardening_Date`,
                        `Sapling_Transplant_Date`)
                        VALUES

                        ({},'{}',{},'{}',{},'{}','{}','{}'); '''.format(request.form['attempt_id'],request.form['date'],request.form['average_germination_duration'],request.form['average_time_of_true_leaves'],request.form['average_sapling_height'],request.form['hardening_cycle'],request.form['hardening_date'],request.form['sapling_transplant_date']))
                flash("Record Inserted ","Success")
            except Exception as e:
                flash("Germination Data:"+str(e),"error")
            return redirect(url_for('admin.germinationweekly'))


        return redirect(url_for('admin.germinationweekly'))
    
@admin.route('/germination_data',methods=['GET','POST'])
def germination_data():
    if request.method == "POST":
        if 'submit' in request.form:
            gdata  = mysql_query('select * from germination_weekly where GID={}'.format(request.form['GID'] ))
            data=mysql_query("select germination.GID,germination.Attempt_Name,germination.location,germination.Plant_Name from germination where GID={}".format(request.form['GID']))
            # return redirect(url_for('admin.germination_data',gdata=gdata))
            return render_template('admin/germinationdata.html',data = data,gdata=gdata)
        if 'delete' in request.form:
            mysql_query("delete from germination_weekly where DID={}".format(request.form['update']))
            flash("DID: "+str(request.form['update'])+" Deleted","success")
            return redirect(url_for('admin.germination_data'))
        if 'update' in request.form:
            mysql_query('''UPDATE `contra`.`germination_weekly`
                            SET
                            `Date` ='{}',
                            `Period` ='{}',
                            `Volume` ={} ,
                            `Time` ={} ,
                            `Dosage_EC` ={} ,
                            `Dosage_PH` ={} ,
                            `Pesticide` = {},
                            `Pesticide_Volume` ={}
                            WHERE `DID` ={}; '''.format(request.form['date'],request.form['period'],request.form['volume'],request.form['time'],request.form['dosage_ec'],request.form['dosage_ph'],request.form['pesticide'],request.form['pesticide_volume'],request.form['update'] ))
            flash("DID: "+str(request.form['update'])+" Updated","success")
            return redirect(url_for('admin.germination_data'))
        
        return "POST"
    
    data=mysql_query("select germination.GID,germination.Attempt_Name,germination.location,germination.Plant_Name from germination")
    print(data)
    return render_template('admin/germinationdata.html',data=data)



@admin.route('/sensordata')
def sensordata():
    data = mysql_query("select boards.Name,sensor_data.Humidity_Sensor,sensor_data.Sound_sensor,sensor_data.Temperature_Sensor,sensor_data.Ultrasonic_sensor,sensor_data.Timestamp as 'Log' from sensor_data inner join boards on boards.BID = sensor_data.BID order by Timestamp desc;")
    return render_template("admin/sensordata.html",data=data)