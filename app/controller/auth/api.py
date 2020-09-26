from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for
import secrets
from werkzeug.datastructures import ImmutableMultiDict
# from ..sqlq import *

api = Blueprint('api',
                __name__,
                url_prefix='/api/v1')

@api.route('/')
def apiindex():
    page = request.args
    page = page.to_dict(flat=False)
#   filter = request.args.get('filter', default = '*', type = str)
#   data = (page,filter)print(page.iterlists())
    return str(page)