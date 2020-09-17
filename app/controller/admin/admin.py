from flask import Flask, render_template, Blueprint, request, g, session, redirect, url_for


admin = Blueprint('admin',
                __name__,
                template_folder="admin_templates",
                static_folder="admin_static",
                url_prefix='/admin')

@admin.route('/')
def index():
    return 'index'