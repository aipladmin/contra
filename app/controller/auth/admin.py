from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for
import secrets
from werkzeug.datastructures import ImmutableMultiDict
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
                            `Un_Soaked_Seeds`,
                            `Total`,
                            `Germination_Date`,
                            `Avg_Germination_Duration`,
                            `Avg_True_Leaves`,
                            `Avg_Sapling_Height`,
                            `Sapling_Transplant_Date`)
                            VALUES
                            ('{}','{}','{}',{},{},{},'{}','{}','{}','{}','{}',{},{},{},'{}',{},{},{},'{}');'''
                            .format(request.form['attemptname'],request.form['location'],request.form['plantname'],
                            request.form['Cocopeatecvalue'],request.form['waterph'],request.form['watertds'],request.form['sowingdate'],
                            request.form['growmedium'],request.form['lightsource'],request.form['seedcompany'],request.form['svariety'],
                            request.form['soakedseeds'],request.form['unsoakedseeds'],request.form['total'],
                            request.form['germinationdate'],request.form['avgerminationduration'],request.form['averagetimeoftrueleaves'],
                            request.form['averagesaplingheight'],request.form['saplingtransplantdate'] ) )
        return "post"
    return "germination_scr"

@admin.route('/germinationweekly')
def germinationweekly():
    data = mysql_query("select *,date(convert_tz(now(),'+00:00','+05:30')) as 'Curdate' from germination;")
    return render_template('admin/germinationlist.html',data=data)

@admin.route('/germinationweekly_scr',methods=['POST'])
def germinationweekly_scr():
    if request.method == "POST":

          if 'weekly' in request.form:
            mysql_query("insert into germination_weekly(GID,Date,Period,Time,Volume,Dosage_EC,Dosage_PH,Pesticide,Pesticide_Volume) values({},'{}','{}','{}',{},{},{},'{}',{});"
                .format(request.form['attempt_id'],request.form['date'],request.form['period_of_time'],request.form['time'],request.form['volume'],request.form['dosage_ec'],request.form['dosage_ph'],request.form['pesticide'],request.form['pesticide_volume'] ) ) 
            return redirect(url_for('admin.germinationweekly'))
        if 'germination_desc' in request.form:
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
            return redirect(url_for('admin.germinationweekly'))

        return redirect(url_for('admin.germinationweekly'))
        
        # period = request.form['period_of_time']
        # if period.lower() == "morning":
        #     mysql_query("insert into days(GID,date,Morning_Dosage_Time,Morning_Dosage_Volume,Evening_Dosage_Time,Evening_Dosage_Volume,Dosage_EC,Dosage_PH) values({},'{}',{},{},{},{},{},{});"
        #                 .format(request.form['attempt_id'],request.form['date'],request.form['period_of_time']) )
        
    return "germinationweekly_scr"

@admin.route('/sensordata')
def sensordata():
    data = mysql_query("select boards.Name,sensor_data.Humidity_Sensor,sensor_data.Sound_sensor,sensor_data.Temperature_Sensor,sensor_data.Ultrasonic_sensor,sensor_data.Timestamp as 'Log' from sensor_data inner join boards on boards.BID = sensor_data.BID order by Timestamp desc;")
    return render_template("admin/sensordata.html",data=data)