from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for,Response,make_response
import secrets
import sys
from werkzeug import exceptions
from werkzeug.datastructures import ImmutableMultiDict
from ..sqlq import *

api = Blueprint('api',
                __name__,
                url_prefix='/api/v1')

@api.route('/')
def apiindex():
    try:
        page = request.args
        page = page.to_dict(flat=False)
        data = mysql_query("select bid from boards where UBID='{}';".format(page['UBID'][0]))
        data = int(data[0]['bid'])
        print(data)
        sensor_data=[]
        str(page['UBID'][0])
        column_names = list(page.keys())

        sd = []
        ad=[]
        for x in column_names:
            # print(x)
            dt = page.get(x)
            # print(dt[0])

            sd.append(dt)
        
        for x in sd[1:]:
            print(x[0])
            z = int(x[0])
            ad.append(z)
        ad.insert(0,data)
        ad = tuple(ad)
        print(ad)
        column_names.insert(1,'BID')
        column_names = tuple(column_names)
        print(column_names[1:])
        mysql_query("insert into sensor_data({}) values{}".format(",".join(column_names[1:]) ,ad))
          # status_code = flask.Response(status=201)
        return  make_response(str(200))
    except :
        return str(sys.exc_info()[0])
    