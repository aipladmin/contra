from flask import Flask, render_template, Blueprint, request, session, redirect, url_for, abort, jsonify,flash
from datetime import date, datetime
import secrets,json,pdfkit,traceback
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
from ..controller import *
from .Data_Analysis import *

admin = Blueprint('admin',
                __name__,
                template_folder="auth_templates",
                static_folder="auth_static",
                url_prefix='/admin')

import platform
if platform.system().lower() == "linux":
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
elif platform.system().lower() == "windows":
    config = pdfkit.configuration(wkhtmltopdf='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe')
WKHTML_Config = config

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

@admin.route('/boards')
def boards():
    api_endpoint =request.host_url
    arduinoID = secrets.token_hex(32)
    sensor_data = mysql_query('select SID,sensor_name from sensor_master;')
    boards = mysql_query("select distinct(boards.BID) as 'identifier',boards.Name,boards.UBID from boards inner join module on module.BID = boards.BID order by boards.BID ASC;")
    sensors = mysql_query('select boards.BID,module.mid,sensor_master.Sensor_Name,sensor_master.Type from module inner join boards on module.BID=boards.BID inner join sensor_master on sensor_master.SID = module.SID order by boards.BID ASC;')
    
    return render_template('admin/boards.html',arduinoID = arduinoID,sensor_data=sensor_data,boards=boards,sensors=sensors)

@admin.route('/boardscr',methods=['GET','POST'])
@login_required
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
@login_required
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
@login_required
def germination():
    return render_template('admin/germination.html')

#! GERMINATION 
####################################################GERMINATION SAPLING
@admin.route('/germination_sapling',methods=['GET','POST'])
@login_required
def germination_sapling():
    if request.method =="POST":
        
        try:
            if 'submit' in request.form:
                print(request.form)
                PMID = mysql_query("Select PMID from Pallete_Master where Pallete_Name='{}';".format(request.form['pallete_name']))
                # print(PMID[0]['PMID'])
                PMID = PMID[0]['PMID']
                
                GCNID = mysql_query("select GCNID from Grow_Channel_Name where Grow_Channel_Name='{}';".format(request.form['channel_name']))
                print(GCNID)
                
                if GCNID == []:
                    
                    mysql_query("INSERT iNTO Grow_Channel_Name(GMID,GSID,Grow_Channel_Name) values({},{},'{}')".format(
                        request.form['medium'],request.form['system_name'],request.form['channel_name']))
                    GCNID = mysql_query.last_row_id
                    print(GCNID)
                else:
                    GCNID = GCNID[0]['GCNID']
                print("#"*100)
                mysql_query(''' INSERT INTO `contra`.`Grow_Channel`
                                    (PMID,
                                    GCNID,
                                    `Netpod`,
                                    `Description`,
                                    `Quantity`)
                                    VALUES
                                    ({},{},'{}','{}',{});
                                    '''.format(PMID,GCNID,request.form['netpod'],request.form['description'],request.form['quantity']))
            if 'final_submit' in request.form:
                mysql_query("UPDATE `contra`.`Grow_Channel` SET `Flag` = 'UPD';")
                flash("Records Stored and Freezed.","success")
                return redirect(url_for('admin.germination_sapling'))
        except Exception as e:
            print(traceback.format_exc())
            return "ERROR"
        else:
            flash("Records Inserted","success")
            return redirect(url_for('admin.germination_sapling'))
    data = mysql_query("select distinct(Pallete_Name) as 'PN' from Pallete_Data")
    system = mysql_query("select * from Grow_System")
    medium = mysql_query("select * from Grow_Medium")
    channel_name = mysql_query("select * from Grow_Channel_Name")
    Inserted_data = mysql_query(''' 
                                SELECT 
                                *
                            FROM
                                Grow_Channel
                                    INNER JOIN
                                Grow_Channel_Name ON Grow_Channel_Name.GCNID = Grow_Channel.GCNID
                                    INNER JOIN
                                Grow_System ON Grow_System.GSID = Grow_Channel_Name.GSID
                                    INNER JOIN
                                Grow_Medium ON Grow_Medium.GMID = Grow_Channel_Name.GMID
                                    INNER JOIN
                                Pallete_Master ON Pallete_Master.PMID = Grow_Channel.PMID
                            WHERE
                                Flag = 'INS'; ''')
    return render_template('admin/germination_sapling.html',data=data,system=system,medium=medium,channel_name=channel_name,Inserted_data=Inserted_data)


@admin.route('/germination/AJAX',methods=['GET','POST'])
def germination_ajax():
    if request.method == "POST":
        # print(request.form)
        if request.form['Request_ID'] == '1':
            print(request.form)
            data  =  mysql_query('''SELECT 
                                    Pallete_Master.Pallete_Name,
                                    seeds_master.Seed_Name,
                                    SUM(CASE
                                        WHEN Pallete_Data.method = 'Sowing' THEN 0
                                        WHEN Pallete_Data.method = 'Germination' THEN Pallete_Data.PD_No_of_Cavity * Pallete_Data.PD_No_of_Seeds
                                        ELSE Pallete_Data.PD_No_of_Cavity * Pallete_Data.PD_No_of_Seeds * - 1
                                    END) AS 'Remaining'
                                FROM
                                    Pallete_Data
                                        INNER JOIN
                                    Pallete_Master ON Pallete_Master.PMID = Pallete_Data.PMID
                                        INNER JOIN
                                    Manufacturer_Seeds ON Manufacturer_Seeds.MSID = Pallete_Master.MSID
                                        INNER JOIN
                                    seeds_master ON seeds_master.SEEDSID = Manufacturer_Seeds.SEEDSID
                                WHERE
                                    Pallete_Master.Pallete_Name = '{}'
                                GROUP BY Pallete_Master.Pallete_Name; '''.format(request.form['pallete_name']))
            print(data)
            return jsonify({'result':data[0]})
        return jsonify({'result':"NO Data"})


####################################################GERMINATION SAPLING

@admin.route('/germination_scr',methods=['POST'])
@login_required
def germination_scr():
    if request.method == "POST":
            try:
                AID = mysql_query("select AID from auth where Emailid='{}';".format(session['email']))
                AID = AID[0]['AID']
                gemcode = session['email'][0:3].capitalize()+request.form['attemptname'][0:3].capitalize()+datetime.now().strftime("/%d%m%y/%H/%M/%S")
                print(gemcode)
                mysql_query('''INSERT INTO `contra`.`germination`
                            (AID,`Attempt_Name`,
                            `Location`,Tags,GemCode)
                            VALUES
                            ({},'{}','{}','{}','{}');'''
                            .format(AID,request.form['attemptname'],request.form['location'],request.form['tags'],gemcode))
                flash("Record(s) Inserted","success")
            except Exception as e:
                flash("Error: "+str(e),"failure")

            return redirect(url_for('admin.germination'))
            
    return "germination_scr"

@admin.route('/germinationweekly')
@login_required
def germinationweekly():
    data = mysql_query("select *,date(convert_tz(now(),'+00:00','+05:30')) as 'Curdate' from germination;")
    return render_template('admin/germinationlist.html',data=data)

@admin.route('/germinationweekly_scr',methods=['POST'])
@login_required
def germinationweekly_scr():
    if request.method == "POST":
        if 'weekly' in request.form:
            try:
                print(request.form)
                mysql_query("insert into germination_weekly(GID,Date,Period,Time,Volume,Dosage_EC,Dosage_PH,Pesticide,Pesticide_Volume) values({},'{}','{}','{}',{},{},{},'{}',{});"
                .format(request.form['attempt_id'],request.form['date'],request.form['period_of_time'],request.form['time'],request.form['volume'],request.form['dosage_ec'],request.form['dosage_ph'],request.form['pesticide'],request.form['pesticide_volume'] ) ) 
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
@login_required
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
@login_required
def sensordata():
    data = mysql_query("select boards.Name,sensor_data.Humidity_Sensor,sensor_data.Sound_sensor,sensor_data.Temperature_Sensor,sensor_data.Ultrasonic_sensor,sensor_data.Timestamp as 'Log' from sensor_data inner join boards on boards.BID = sensor_data.BID order by Timestamp desc;")
    return render_template("admin/sensordata.html",data=data)

@admin.route('/reports',methods=['GET','POST'])
@login_required
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
@login_required
def palletes():
    if request.method =="POST":
        try:
            if 'submit' in request.form:
                mysql_query('''INSERT INTO `contra`.`cavities`
                            (`Name`,`No_of_Cavities`)
                            VALUES('{}',{})'''.format(request.form['name'],request.form['no_of_cavities']))
                flash("Data Inserted.","success")
                return redirect(url_for('admin.palletes'))
            if 'update' in request.form:
                mysql_query(''' UPDATE `contra`.`cavities`
                                SET
                                `Name` = '{}',
                                `No_of_Cavities` = {}
                                WHERE `CID` = {};
                                '''.format(request.form['name'],request.form['noc'],request.form['update']))
                flash("Data Updated.","success")
                return redirect(url_for('admin.palletes'))
        except mysql.connector.IntegrityError as e:
            flash("Name Exist: "+e.str(),"danger")
            return redirect(url_for('admin.palletes'))
    palletes = mysql_query("select * from cavities")
    return render_template('admin/GerminationTray.html',cavities=palletes)

@admin.route('/palletinfo',methods=['GET', 'POST'])
@login_required
def palletinfo():
    return "palleteInfo"

####################################### PALLETE DATA       ####################
@admin.route('/palleteData',methods=['GET','POST'])
@login_required
def palleteData():
    if request.method =="POST":
        
        
        MSID =  mysql_query("select * from Manufacturer_Seeds where MID={} and SEEDSID={};".format(request.form['manufacturer'],request.form['seeds']))
        MSID = MSID[0]['MSID']
        
        PMID = mysql_query("select PMID from Pallete_Master where Pallete_Name='{}'".format(request.form['pallete_name']))
        print(PMID)
        
        print(len(PMID))
        if len(PMID) == 0:
            mysql_query(''' INSERT INTO `contra`.`Pallete_Master`
                        (`CID`,
                        `GID`,
                        `MSID`,
                        `Pallete_Name`)
                        VALUES
                        ({},{},{},'{}');
                        '''.format(request.form['pallete_type'],request.form['germination_nameselect * from germination;'],MSID,request.form['pallete_name']))
            PMID=mysql_query.last_row_id

            mysql_query('''INSERT INTO `contra`.`Pallete_Data`
                            (`PMID`,
                            `Method`,
                            `Date`,
                            `PD_No_of_Cavity`,
                            `PD_No_of_Seeds`)
                            VALUES
                            ({},'{}','{}',{},{});'''.format(PMID,request.form['method'],request.form['date'],request.form['noc'],request.form['nofs']))
        else:
            Earlier_PMID = PMID[0]['PMID']
            mysql_query('''INSERT INTO `contra`.`Pallete_Data`
                            (`PMID`,
                            `Method`,
                            `Date`,
                            `PD_No_of_Cavity`,
                            `PD_No_of_Seeds`)
                            VALUES
                            ({},'{}','{}',{},{});'''.format(Earlier_PMID,request.form['method'],request.form['date'],request.form['noc'],request.form['nofs']))


        flash('Data inserted','success')
        return redirect(url_for('admin.palleteData'))
    palletes = mysql_query("select * from cavities")
    manufacturers = mysql_query("select * from Manufacturer_Master")
    seeds = mysql_query("select * from seeds_master")
    Palletes_Name=mysql_query("select distinct(Pallete_Name) from Pallete_Data;")
    germination = mysql_query("select * from germination")
    return render_template('admin/palleteData.html',palletes=palletes,manufacturers=manufacturers,seeds=seeds,Palletes_Name=Palletes_Name,germination=germination)

@admin.route('/PDAJAX',methods=['POST'])
@login_required
def PDAJAX():
    print("READING..........................")
    if request.form['Request_ID'] == "0":
        print(request.form)
        data = mysql_query("Select * from Pallete_Master inner join germination ON germination.GID=Pallete_Master.GID where Pallete_Master.GID={};".format(request.form['germination_id']))
        print(data)
        return jsonify({'result':data})
    if request.form['Request_ID'] == "1":
        print(request.form['method'])
        data = mysql_query(''' SELECT 
                                cavities.No_of_Cavities - SUM(Pallete_Data.PD_No_of_Cavity) AS 'RemPart'
                            FROM Pallete_Data INNER JOIN Pallete_Master ON Pallete_Master.PMID=Pallete_Data.PMID Inner join cavities ON cavities.CID = Pallete_Master.CID
                            WHERE
                                Pallete_Master.Pallete_Name = '{}' AND Pallete_Data.Method = '{}'
                            GROUP BY Pallete_Master.Pallete_Name;'''.format(request.form['pallete'],request.form['method']))

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
        data = mysql_query(''' SELECT 
                                cavities.CID,cavities.Name,
                                seeds_master.SEEDSID,seeds_master.seed_name,
                                Manufacturer_Master.MID,Manufacturer_Master.Company_Name
                            FROM
                                Pallete_Data
                                INNER join
                                Pallete_Master  on Pallete_Master.PMID = Pallete_Data.PMID
                                    INNER JOIN
                                cavities ON Pallete_Master.CID = cavities.CID
                                    INNER JOIN
                                Manufacturer_Seeds ON Manufacturer_Seeds.MSID = Pallete_Master.MSID
                                    INNER JOIN
                                Manufacturer_Master ON Manufacturer_Master.MID = Manufacturer_Seeds.MID
                                INNER JOIN
                                seeds_master ON seeds_master.SEEDSID= Manufacturer_Seeds.SEEDSID
                            WHERE
                                Pallete_Master.Pallete_Name = '{}'
                            LIMIT 1; '''.format(request.form['name']))
        

        if len(data) == 0:
            return jsonify({"result":"0"})
        else:
            return jsonify({"result":data})
####################################### MANUFACTURER DATA    ####################

@admin.route('/manufacturers',methods=['GET','POST'])
@login_required
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
    mdata = mysql_query(''' SELECT 
                ManCode, Company_Name, Purchase_Date, Expiry_Date, Seed_Name
                FROM
                Manufacturer_Seeds
                    INNER JOIN
                Manufacturer_Master ON Manufacturer_Master.MID = Manufacturer_Seeds.MID
                    INNER JOIN
                seeds_master ON seeds_master.SEEDSID = Manufacturer_Seeds.SEEDSID; ''')
    print(mdata)
    return render_template('admin/manufacturers.html',data=data,mdata=mdata)

options = {
        'page-size': 'A4',
        'margin-top': '0.5in',
        'margin-right': '0.75in',
        'margin-bottom': '0.5in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'footer-left': "Contra Farms \nDeveloped by Wizards.",
        'footer-font-size':'7',
        'footer-right': '[page] of [topage]',
        
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None
    }

@admin.route('/viewallPallete')
def palleteReports():
    now = datetime.now()
    # palleteData = mysql_query('select distinct(Pallete_Name) from Pallete_Data')
    # data = mysql_query('''SELECT *,DATE_FORMAT(Date,'%d/%m/%y') AS 'SDATE' FROM
    # Pallete_Data
    #     INNER JOIN
    # Manufacturer_Seeds ON Pallete_Data.MSID = Manufacturer_Seeds.MSID 
	# INNER JOIN
    # Manufacturer_Master ON Manufacturer_Seeds.MID=Manufacturer_Master.MID
    #   INNER JOIN
    # seeds_master ON seeds_master.SEEDSID = Manufacturer_Seeds.SEEDSID;''')
    
    data = report1()

    # rendered = render_template('admin/report_bones.html',data=data,now=now,palleteData=palleteData)
    rendered = render_template('admin/reports_template.html',data=data,now=now,palleteData=palleteData)

    pdf = pdfkit.from_string(rendered,False,configuration=WKHTML_Config,options=options)
    response =make_response(pdf)
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition']='inline'
    return response

@admin.route('/sowingReports')
def sowingReports():
    data = report2()
    return render_template('admin/Reports/sowingReports.html',data_html = data)

@admin.route('/Reports')
def Reports():
    data,plot_histo = RepoDashboard()
    
    return render_template('admin/Reports/Reports.html',data_html = data,plot_histo=plot_histo)