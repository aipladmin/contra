from flask import Flask, render_template, Blueprint, stream_with_context, request
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
    data = mysql_query("select * from Hits.Data")

    return render_template('raw_data.html',data=data)

# @hits.route('/stream')
# def streamed_response():
#     data = mysql_query("select * from Hits.Data")
#     def generate():
#         yield 'Hello '
#         yield data
#         yield '!'
#     for x in generate():
#         return app.response_class(stream_with_context(generate()))