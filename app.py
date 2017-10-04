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
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, send_file, session, url_for, Markup, make_response)
from flask_mail import Mail, Message

import StringIO
from selenium import webdriver
from PIL import Image
import smtplib
import urllib
from werkzeug import secure_filename
from random import randint

from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache

from apps.models.wrapper import Wrapper
from apps.models.users import Users
from apps.models.sites import Sites

SERVER = "localhost"


# Log config
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
# ----------------------------------------------------------------------------

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    sites = Sites(Wrapper()).get_all()

    return render_template('index.html', sites=sites)

@app.route('/site', methods=['GET'])
def site():
    id = request.args.get('id')
    sites = Sites(Wrapper()).get_site(id[0])
    url = sites[0]['url']
    response = requests.get(url)
    robots = requests.get(url + "/robots.txt")
    sitemap = requests.get(url + "/sitemap.xml")
    page = BeautifulSoup(response.content)
    title = page.title
    h1 = page.find('h1')
    robots_content =  BeautifulSoup(robots.content)
    sitemap_content = BeautifulSoup(sitemap.content)
    meta_description =  page.findAll(attrs={"name":"description"})
    #
    # driver = webdriver.PhantomJS(executable_path="node_modules/phantomjs/bin/phantomjs")
    # driver.set_window_size(1366, 2000)  # optional
    # driver.get(url)
    # driver.save_screenshot('static/screen_hires.png')


    return render_template('site.html',
                           sites=sites,
                           title=title,
                           response=response,
                           h1=h1,
                           robots_content=robots_content,
                           meta_description=meta_description,
                           sitemap_content=sitemap_content)


@app.route('/test')
def test():
    server = smtplib.SMTP(SERVER, 1025)
    server.sendmail('olhahryhorenko@gmail.com', 'olhahryhorenko@gmail.com', "msg")
    server.quit()
    return 'sent'



if __name__ == "__main__":
    app.run(debug=True)
else:
    logging.basicConfig(debug=True, threaded=True,host='0.0.0.0', port=5000)
