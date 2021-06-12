from flask import Flask, render_template, Blueprint
from datetime import date, datetime
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from datetime import datetime, timedelta
from ..controller import *


hits = Blueprint('hits',
                __name__,
                template_folder="auth_templates",
                static_folder="auth_static",
                url_prefix='/hits')

@hits.route('/')
@hits.route('/index')
def getData():
    data = mysql_query("select DID,ID,Meters,convert_tz(Timestamp,'+00:00','+5:30') as 'IST',Timestamp - LAG(Timestamp) OVER (ORDER BY Timestamp) AS Timestamps_since_last_case from Hits.Data ORDER BY Timestamp;")

    return render_template('raw_data.html',data=data)
