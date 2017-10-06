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
import schedule
import string
import requests
from pytz import timezone
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from threading import Thread
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

start_time = time.time()




def login_required(f):
    @wraps(f)
    def wrap():
        if session['logged_in'] == True:
            return f()
        else:
            abort(404)

    return wrap


@app.route('/', methods=['GET'])
def index():
    sites = Sites(Wrapper()).get_all()
    if session['logged_in'] == True:
        return redirect(url_for('main'))
    else:
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


@app.route('/logout',  methods=['GET'])
def logout():
    session['id'] = None
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/main')
@login_required
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
    response_code = response.status_code
    robots = requests.get(url + "/robots.txt")
    sitemap = requests.get(url + "/sitemap.xml")
    page = BeautifulSoup(response.content)

    title = page.title
    h1 = page.find('h1')
    robots_content = BeautifulSoup(robots.content)
    html = page.prettify()

    sitemap_content = BeautifulSoup(sitemap.content)
    meta_description = page.find("meta", {"name": "description"})['content']
    meta_robots = "robots"
    # meta_title = page.find("meta", {"name": "title"})['content']

    add_site_data = SiteData(Wrapper()).add_site_data({"site_id": add_new, "title": title, "h1": h1,
                                                       "meta_description": meta_description,
                                                       "meta_title": "meta_title",
                                                       "meta_robots":"",
                                                       "html": escape_string(str(html)),
                                                       "response": response_code,
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



@app.route("/site-delete")
def delete():
    id = request.args.get('id')
    delete_data = SiteData(Wrapper()).delete_site_data(id)
    delete = Sites(Wrapper()).delete_site(id)
    return jsonify(delete)


def check_status():
    id = "54"
    site = Sites(Wrapper()).get_site(id)
    url = site[0]['url']

    #from db

    site_data = SiteData(Wrapper()).get_site_data(id)
    response_code = site_data[0]['response']
    sitemap = site_data[0]['robots']
    html = site_data[0]['html']
    title = site_data[0]['title']
    h1 = site_data[0]['h1']
    robots_content = site_data[0]['robots']
    sitemap_content = site_data[0]['sitemap']
    meta_description = site_data[0]['meta_description']


    #current response
    current_response = requests.get(url)
    current_response_code = current_response.status_code
    current_robots = requests.get(url + "/robots.txt")
    current_sitemap = requests.get(url + "/sitemap.xml")
    current_page = BeautifulSoup(current_response.content)
    current_title = current_page.title
    current_h1 = current_page.find('h1')
    current_robots_content =  BeautifulSoup(current_robots.content)
    current_sitemap_content = BeautifulSoup(current_sitemap.content)
    current_meta_description = current_page.find("meta", {"name": "description"})['content']

    if str(response_code) != str(current_response_code):
        send_mail("response code not the same")
    else:
        send_mail("response code  the same")
    return True


def check_status_code():
    id = "54"
    site = Sites(Wrapper()).get_site(id)
    url = site[0]['url']
    site_data = SiteData(Wrapper()).get_site_data(id)
    response_code = site_data[0]['response']
    current_response = requests.get(url)
    current_response_code = current_response.status_code
    if str(response_code) != str(current_response_code):
        send_mail("response code not the same")
    else:
        send_mail("response code  the same")
    return True


def send_mail(text):
    msg = text
    smtp = SMTP()
    smtp.connect("mbxsrv.com")
    smtp.login("o.grigorenko@bryteq.com", "GueUhmXg")
    smtp.sendmail("olhahryhorencko@gmail.com", "olhahryhorencko@gmail.com", msg)
    # ##logging.info("from_address = {0}".format(from_address))
    smtp.quit()
    return '1'



if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(debug=True)
else:
    logging.basicConfig(debug=True, threaded=True,
                        host='0.0.0.0', port=5000)





