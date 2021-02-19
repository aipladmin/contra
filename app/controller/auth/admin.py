from flask import Flask, render_template, Blueprint, request, session, redirect, url_for, abort, jsonify,flash
import secrets,json
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
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
            mysql_query("delete from germination_weekly where DID={}".format(request.form['delete']))
            flash("DID: "+str(request.form['delete'])+" Deleted","success")
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

@admin.route('/reports',methods=['GET','POST'])
def reports():
    if request.method == "POST":
        gdata  = mysql_query('select * from germination_weekly where GID={}'.format(request.form['GID'] ))
        data=mysql_query("select germination.GID,germination.Attempt_Name,germination.location,germination.Plant_Name from germination where GID={}".format(request.form['GID']))
            # return redirect(url_for('admin.germination_data',gdata=gdata))
        return render_template('admin/reports.html',data = data,gdata=gdata)

    data=mysql_query("select germination.GID,germination.Attempt_Name,germination.location,germination.Plant_Name from germination")
    print(data)
    return render_template('admin/reports.html',data=data)

@admin.route('/palletes',methods=['GET','POST'])
def palletes():
    if request.method =="POST":
        try:
            mysql_query('''INSERT INTO `contra`.`cavities`
                        (`Name`,`No_of_Cavities`)
                        VALUES('{}',{})'''.format(request.form['name'],request.form['no_of_cavities']))
            flash("Data Inserted","success")
            return redirect(url_for('admin.palletes'))
        except mysql.connector.IntegrityError as e:
            flash("Name Exist: "+e.str(),"danger")
            return redirect(url_for('admin.palletes'))
    return render_template('admin/palletes.html')
####################################### PALLETE DATA       ####################
@admin.route('/palleteData',methods=['GET','POST'])
def palleteData():
    if request.method =="POST":
        MSID =  mysql_query("select * from Manufacturer_Seeds where MID={} and SEEDSID={};".format(request.form['manufacturer'],request.form['seeds']))
        MSID = MSID[0]['MSID']
        mysql_query('''INSERT INTO `contra`.`Pallete_Data`
                        (`MSID`,
                        `CID`,
                        `Pallete_Name`,
                        `Method`,
                        `Date`,
                        `PD_No_of_Cavity`,
                        `PD_No_of_Seeds`)
                        VALUES
                        ({},{},'{}','{}','{}',{},{});'''.format(MSID,request.form['pallete_type'],request.form['pallete_name'],request.form['method'],request.form['date'],request.form['noc'],request.form['nofs']))
        return "render_template"
    palletes = mysql_query("select * from cavities")
    manufacturers = mysql_query("select * from Manufacturer_Master")
    seeds = mysql_query("select * from seeds_master")
    Palletes_Name=mysql_query("select Pallete_Name from Pallete_Data;")
    return render_template('admin/palleteData.html',palletes=palletes,manufacturers=manufacturers,seeds=seeds,Palletes_Name=Palletes_Name)

@admin.route('/PDAJAX',methods=['POST'])
def PDAJAX():
    print("READING..........................")
    if request.form['Request_ID'] == "1":
        print(request.form['method'])
        data = mysql_query(''' SELECT 
                                cavities.No_of_Cavities - SUM(Pallete_Data.PD_No_of_Cavity) AS 'RemPart'
                            FROM Pallete_Data INNER JOIN cavities ON cavities.CID = Pallete_Data.CID
                            WHERE
                                Pallete_Data.Pallete_Name = '{}' AND Pallete_Data.Method = '{}'
                            GROUP BY Pallete_Name;'''.format(request.form['pallete'],request.form['method']))
        if len(data) == 0:
            return jsonify({"result":"50"})
        else:
            data = str(data[0]['RemPart'])
            return jsonify({"result":data})
    elif request.form['Request_ID'] == "2":
        data = mysql_query("select Manufacturer_Master.MID,Manufacturer_Master.Company_Name  from Manufacturer_Master inner join Manufacturer_Seeds ON Manufacturer_Master.MID=Manufacturer_Seeds.MID where Manufacturer_Seeds.SEEDSID={}".format(request.form['seeds']))
        # data = data[0]
        print(data)
        return jsonify({"result":data})
    elif request.form['Request_ID'] == "3":
        print(request.form['name'])
        data = mysql_query("select * from Pallete_Data where Pallete_Name='{}' limit 1;".format(request.form['name']))
        print(data)
        if len(data) == 0:
            return jsonify({"result":"0"})
        else:
            return jsonify({"result":data})
####################################### PALLETE DATA       ####################

@admin.route('/manufacturers',methods=['GET','POST'])
def manufacturers():
    if request.method == 'POST':
        try:

            pur_date = datetime.strptime(request.form['pur_date'],"%Y-%m-%d")
            exp_date = datetime.strptime(request.form['exp_date'],"%Y-%m-%d")
            purdate = pur_date.strftime('%d%m')
            exp_date =exp_date.strftime('%d%m')
            
            com_name=request.form['company_name'][:3].strip()
            seeds = mysql_query("select Seed_Name from seeds_master where SEEDSID='{}';".format(request.form['seedsid']))
            seeds = seeds[0]['Seed_Name'][:3].strip()
            ManuCode = com_name+"/"+seeds+"/"+purdate+"/"+exp_date
            ManCode = ManuCode.upper()

            mysql_query('''INSERT INTO `contra`.`Manufacturer_Master`
                        (`ManCode`,
                        `Company_Name`,
                        `No_of_Seeds`,
                        `Variety`,
                        `Purchase_Date`,
                        `Expiry_Date`,
                        `Weight`,
                        `Price`)
                        VALUES
                        ('{}','{}',{},'{}','{}','{}',{},{})'''.format(ManCode,request.form['company_name'],request.form['no_of_seeds'],request.form['variety'],request.form['pur_date'],request.form['exp_date'],request.form['weight'],request.form['price']))
            MID =  mysql_query.last_row_id
            mysql_query("insert into Manufacturer_Seeds(MID,SEEDSID) values({},{});".format(MID,request.form['seedsid']))
            flash("Records Inserted.","success")
            return redirect(url_for('admin.manufacturers'))
        except Exception as e:
            flash("Error:"+str(e),"danger")
            return redirect(url_for('admin.manufacturers'))
        
    data = mysql_query("select * from seeds_master")
    return render_template('admin/manufacturers.html',data=data)