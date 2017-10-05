#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import logging
import os
import random
import time
import pytz
import glob
import string
import requests
from pytz import timezone
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from functools import wraps
from smtplib import SMTP_SSL, SMTP
from time import gmtime, strftime
from MySQLdb import escape_string

import magic
import urllib2

import pygeoip
from BeautifulSoup import BeautifulSoup
from flask import (Flask, Response, abort, jsonify, redirect, flash, render_template,
                   request, send_file, session, url_for, Markup, make_response)
from flask_mail import Mail, Message

import StringIO
from selenium import webdriver
from PIL import Image
import xml2json
import smtplib
import urllib
from werkzeug import secure_filename
from random import randint

from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
from flask.ext.session import Session

from apps.models.wrapper import Wrapper
from apps.models.users import Users
from apps.models.sites import Sites
from apps.models.site_data import SiteData


SERVER = "localhost"


# Log config
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
# ----------------------------------------------------------------------------

app = Flask(__name__)
sess = Session()




# def login_required(f):
#     @wraps(f)
#     def wrap():
#         if 'logged_in' in session:
#             return f()
#         else:
#             abort(404)
#
#     return wrap


@app.route('/', methods=['GET'])
def index():
    sites = Sites(Wrapper()).get_all()

    return render_template('index.html', sites=sites)


@app.route('/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    log_in = Users().login({'login': login, 'password': password})
    if log_in == False:
        flash('This message gets lost')  # this message gets lost
        return redirect(url_for('index'))
    user_id = Users().get_user_id(login)
    session['id'] = user_id[0].get('id')
    session['logged_in'] = True
    return redirect(url_for('main'))


@app.route('/main')
def main():
    user = Users().get_user(session['id'])
    sites = Sites(Wrapper()).get_all_for_user(session['id'])
    return render_template('main.html',
                           user=user,
                           sites=sites)


@app.route('/add_new', methods=['POST'])
def add_new():
    url = escape_string(request.form.get('url'))
    user_id = session['id']
    curdatetime = time.strftime("%Y-%m-%d %H:%M:%S")
    add_new = Sites(Wrapper()).add_site({"url": url, "user_id": user_id, "date": curdatetime})

    # get site info
    response = requests.get(url)
    robots = requests.get(url + "/robots.txt")
    sitemap = requests.get(url + "/sitemap.xml")
    page = BeautifulSoup(response.content)

    title = page.title
    h1 = page.find('h1')
    robots_content = BeautifulSoup(robots.content)
    sitemap_content = BeautifulSoup(sitemap.content)
    meta_description = page.findAll(attrs={"name": "description"})
    meta_robots = "robots"
    meta_title = page.findAll(attrs={"name": "title"})

    add_site_data = SiteData(Wrapper()).add_site_data({"site_id": add_new, "title": title, "h1": h1,
                                                       "meta_description": 'rob', "meta_title": meta_title,
                                                       "meta_robots":"",
                                                       "response": response,
                                                       "robots": robots_content,
                                                       "sitemap": escape_string(str(sitemap_content))})

    if add_new == "-1":
        flash('Error.Try again')  # this message gets lost
        return redirect(url_for('main'))
    return redirect(url_for('main'))


@app.route('/site', methods=['GET'])
def site():
    # current response
    id = request.args.get('id')

    # current response
    site = Sites(Wrapper()).get_site(id)
    # url = sites[0]['url']
    #
    # response = requests.get(url)
    # robots = requests.get(url + "/robots.txt")
    # sitemap = requests.get(url + "/sitemap.xml")
    # page = BeautifulSoup(response.content)
    # title = page.title
    # h1 = page.find('h1')
    # robots_content =  BeautifulSoup(robots.content)
    # sitemap_content = BeautifulSoup(sitemap.content)
    # meta_description =  page.findAll(attrs={"name":"description"})
    #
    # driver = webdriver.PhantomJS(executable_path="node_modules/phantomjs/bin/phantomjs")
    # driver.set_window_size(1366, 2000)  # optional
    # driver.get(url)
    # driver.save_screenshot('static/screen_hires.png')

    # from db

    sites_data = SiteData(Wrapper()).get_site_data(id)

    return render_template('site.html',
                           site=site,
                           sites_data=sites_data)
                           # title=title,
                           # response=response,
                           # h1=h1,
                           # robots_content=robots_content,
                           # meta_description=meta_description,
                           # sitemap_content=sitemap_content)


@app.route('/test')
def test():
    server = smtplib.SMTP(SERVER, 1025)
    server.sendmail('olhahryhorenko@gmail.com', 'olhahryhorenko@gmail.com', "msg")
    server.quit()
    return 'sent'



if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    app.run(debug=True)
else:
    logging.basicConfig(debug=True, threaded=True,host='0.0.0.0', port=5000)
