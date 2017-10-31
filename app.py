#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import logging

import time

import requests
import atexit
import socket

from functools import wraps
from smtplib import SMTP_SSL, SMTP

from MySQLdb import escape_string

from BeautifulSoup import BeautifulSoup

from flask import (Flask, Response, abort, jsonify, redirect, flash, render_template,
                   request, send_file, session, url_for, Markup, make_response)

from apps.models.wrapper import Wrapper
from apps.models.users import Users
from apps.models.sites import Sites
from apps.models.site_data import SiteData
from apps.models.statuses import Statuses



# Log config
# logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
# ----------------------------------------------------------------------------

app = Flask(__name__)

app.secret_key = 'sss'
app.permanent_session_lifetime = datetime.timedelta(days=64)
site_mail = 'o.grigorenko@bryteq.com'
logging.basicConfig()
start_time = time.time()


def job_function():
    print "Hello World"


@app.route('/set/')
def set():
    session['logged_in'] = False
    session['id'] = None
    return 'ok'


def login_required(f):
    @wraps(f)
    def wrap():
        if 'logged_in' in session:
            return f()
        else:
            abort(404)
    return wrap


@app.route('/', methods=['GET'])
def index():
    if bool(session) == False:
        return render_template('index.html')
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    log_in = Users().login({'login': login, 'password': password})
    if log_in == False:
        flash('There is no user with such credential. Try again')  # this message gets lost
        return redirect(url_for('index'))
    user_id = Users().get_user_id(login)
    session['id'] = user_id[0].get('id')
    session['logged_in'] = True
    return redirect(url_for('main'))


@app.route('/logout',  methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/main')
@login_required
def main():
    user = Users().get_user(session['id'])
    sites = Sites(Wrapper()).get_all_for_user(session['id'])
    statuses = Statuses(Wrapper()).get_status_for_all()
    return render_template('main.html',
                           user=user,
                           statuses=statuses,
                           sites=sites)


@app.route('/get-status', methods=['GET'])
def check_status_by_id():
    id = request.args.get('id')
    status = Statuses(Wrapper()).get_status(id)

    return jsonify(len(status))


@app.route('/settings')
@login_required
def settings():
    user = Users().get_user(session['id'])
    print user
    return render_template('settings.html', user=user)


@app.route('/update-setting', methods=['POST'])
@login_required
def update_settings():
    login = request.form.get('login')
    email = request.form.get('email')
    user = Users().edit_user({"login": login, "email": email}, session['id'])
    flash("Changes saved")
    return redirect(url_for('settings'))


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

    title = page.title.text
    h1 = page.find('h1')
    robots_content = BeautifulSoup(robots.content)
    html = page.prettify()

    sitemap_content = BeautifulSoup(sitemap.content)
    meta_description = page.find("meta", {"name": "description"})['content']
    clear_url = url.replace("https://", "").strip("/")
    ip = socket.gethostbyname(clear_url)

    meta_robots = "robots"
    # meta_title = page.find("meta", {"name": "title"})['content']
    add_site_data = SiteData(Wrapper()).add_site_data({"site_id": add_new,
                                                       "h1": h1,
                                                       "title": title,
                                                       "response_code": response_code,
                                                       "meta_robots": robots_content,
                                                       "sitemap": escape_string(str(sitemap_content)),
                                                       "html": escape_string(str(html)),
                                                       "meta_description": meta_description,
                                                       "ip": ip,
                                                       "date": curdatetime
                                                       })

    if add_site_data == "-1":
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
    statuses = Statuses(Wrapper()).get_status(id)

    return render_template('site.html',
                           site=site,
                           statuses=statuses,
                           sites_data=sites_data)



@app.route('/get-sitemap', methods=['GET'])
def sitemap():
    id = request.args.get('id')
    sitemap = SiteData(Wrapper()).get_site_sitemap(id)
    return render_template('sitemap.html',
                           sitemap=sitemap[0]['sitemap'])


@app.route('/get-html', methods=['GET'])
def html():
    id = request.args.get('id')
    html = SiteData(Wrapper()).get_site_html(id)
    return render_template('html.html',
                           html=html[0]['html'])



@app.route('/site-statistic', methods=['GET'])
def site_statistic():
    id = request.args.get('id')
    site = Sites(Wrapper()).get_site(id)
    statuses = Statuses(Wrapper()).get_status(id)
    return render_template('statistic.html', statuses=statuses,
                           site=site)


@app.route("/site-delete")
def delete():
    id = request.args.get('id')
    delete_data = SiteData(Wrapper()).delete_site_data(id)
    delete = Sites(Wrapper()).delete_site(id)
    return jsonify(delete)


@app.route("/check-sites")
def check_status():
    curdatetime = time.strftime("%Y-%m-%d %H:%M:%S")
    sites = Sites(Wrapper()).get_all()
    for site in sites:
        url = site['url']
        id = site['id']
        response = requests.get(url)
        response_code = response.status_code
        page = BeautifulSoup(response.content)

        #check titles
        title = SiteData(Wrapper()).get_sites_title(id)
        current_title = page.title
        print title[0]['data']
        if str(current_title) != title[0]['data']:
            print "changed"
            send_mail("Current title changed on {0} on {1}".format(current_title, url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "1",
                                                     "data": "Current title %s" % current_title})
        else:
            print 'not changed'

        # check h1
        h1 = SiteData(Wrapper()).get_sites_h1(id)
        current_h1 = page.find('h1')
        # print str(h1[0]['data'])
        # print str(current_h1)
        if str(current_h1) != str(h1[0]['data']):
            print 'changed'
            send_mail("Current h1 %s" % current_h1)
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime,"type_id": "2",
                                                     "data": "Current h1 %s" % current_h1})
        else:
            print "not changed"

        # check get_sites_description
        description = SiteData(Wrapper()).get_sites_description(id)
        current_description = page.find("meta", {"name": "description"})['content']
        # print str(description[0]['data'])
        # print str(current_description)
        if str(current_description) != str(description[0]['data']):
            print 'changed'
            send_mail("Current description is {0} on {1}".format(current_description, url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "4",
                                                     "data": "Current description %s" % current_description})
        else:
            print "not changed"


        # check get_sites_sitemap
        sitemap = SiteData(Wrapper()).get_sites_sitemap(id)
        current_sitemap = requests.get(url + "/sitemap.xml")
        current_sitemap_content = BeautifulSoup(current_sitemap.content)
        if str(current_sitemap_content) != str(sitemap[0]['data']):
            print 'changed'
            send_mail("Current sitemap changed on {0}".format(url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "7",
                                                     "data": "Current sitemap changed"})
        else:
            print "not changed"

        # check get_sites_html
        html = SiteData(Wrapper()).get_sites_html(id)
        page = BeautifulSoup(response.content)
        current_html = page.prettify()

        if str(current_html) != str(html[0]['data']):
            print 'changed'
            send_mail("Current html changed on %s" % url)
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "8",
                                                     "data": "Current html changed"})
        else:
            print "not changed"

        # check ip
        ip = SiteData(Wrapper()).get_sites_ip(id)
        clear_url = url.replace("https://", "").strip("/")
        current_ip = socket.gethostbyname(clear_url)
        if str(current_ip) != str(ip[0]['data']):
            print 'changed'
            send_mail("Current ip changed on %s" % url)
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "8",
                                                     "data": "Current ip changed for %s" % current_ip})
        else:
            print "not changed"
    send_mail('Everyday check was done successfully {0}'.format(curdatetime))
    return "Check done"

    # #from db
    #
    # site_data = SiteData(Wrapper()).get_site_data(id)
    # response_code = site_data[0]['response']
    # sitemap = site_data[0]['robots']
    # html = site_data[0]['html']
    # title = site_data[0]['title']
    # h1 = site_data[0]['h1']
    # robots_content = site_data[0]['robots']
    # sitemap_content = site_data[0]['sitemap']
    # meta_description = site_data[0]['meta_description']
    #
    #
    # #current response
    # current_response = requests.get(url)
    # current_response_code = current_response.status_code
    # current_robots = requests.get(url + "/robots.txt")
    # current_sitemap = requests.get(url + "/sitemap.xml")
    # current_page = BeautifulSoup(current_response.content)
    # current_title = current_page.title
    # current_h1 = current_page.find('h1')
    # current_robots_content =  BeautifulSoup(current_robots.content)
    # current_sitemap_content = BeautifulSoup(current_sitemap.content)
    # current_meta_description = current_page.find("meta", {"name": "description"})['content']
    #
    # if str(response_code) != str(current_response_code):
    #     send_mail("response code not the same")
    # else:
    #     send_mail("response code  the same")
    # return True


def check_status_code():
    curdatetime = time.strftime("%Y-%m-%d %H:%M:%S")
    sites = Sites(Wrapper()).get_all()
    for site in sites:
        url = site['url']
        id = site['id']
        response = requests.get(url)
        page = BeautifulSoup(response.content)
        # check response
        response_code = SiteData(Wrapper()).get_sites_response(id)
        current_response = requests.get(url)
        current_response_code = current_response.status_code
        if str(current_response_code) != str(response_code[0]['data']):
            print 'changed'
            send_mail("Response code on {0} not the same. It is {1}".format(url, current_response_code))
            current_response = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                               "date": curdatetime, "type_id": "3",
                                                               "data": "Current response %s" % current_response_code})
        else:
            print "not changed"
    return True


def send_mail(msg):
    smtp = SMTP()
    smtp.connect("mbxsrv.com")
    smtp.login("o.grigorenko@bryteq.com", "GueUhmXg")
    smtp.sendmail("noreply@bryteq.com", "olhahryhorencko@gmail.com", msg)
    # ##logging.info("from_address = {0}".format(from_address))
    smtp.quit()
    return '1'


@app.route('/test')
def test():
    curdatetime = time.strftime("%Y-%m-%d %H:%M:%S")
    sites = Sites(Wrapper()).get_all()
    for site in sites:
        url = site['url']
        id = site['id']
        # get site info
        response = requests.get(url)
        response_code = response.status_code
        robots = requests.get(url + "/robots.txt")
        sitemap = requests.get(url + "/sitemap.xml")
        page = BeautifulSoup(response.content)

        title = page.title.text
        h1 = page.find('h1')
        robots_content = BeautifulSoup(robots.content)
        html = page.prettify()

        sitemap_content = BeautifulSoup(sitemap.content)
        meta_description = page.find("meta", {"name": "description"})['content']
        clear_url = url.replace("https://", "").strip("/")
        ip = socket.gethostbyname(clear_url)

        meta_robots = "robots"
        # meta_title = page.find("meta", {"name": "title"})['content']
        add_site_data = SiteData(Wrapper()).add_site_data({"site_id": id,
                                                           "h1": h1,
                                                           "title": title,
                                                           "response_code": response_code,
                                                           "meta_robots": robots_content,
                                                           "sitemap": escape_string(str(sitemap_content)),
                                                           "html": escape_string(str(html)),
                                                           "meta_description": meta_description,
                                                           "ip": ip,
                                                           "date": curdatetime
                                                           })
        site_data = SiteData(Wrapper()).get_site_data_by_id(add_site_data)
        last_record = SiteData(Wrapper()).get_last_record(id)
        # check titles
        if str(last_record[0]['title']) != str(site_data[0]['title']):
            print "changed"
            send_mail("Current title changed on {0} on {1}".format(site_data[0]['title'], url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "1",
                                                     "data": "Current title %s" % site_data[0]['title']})
        else:
            print 'not changed'

        # check h1
        if str(last_record[0]['h1']) != str(site_data[0]['h1']):
            print 'changed'
            send_mail("Current h1 %s" % add_site_data[0]['h1'])
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "2",
                                                     "data": "Current h1 %s" % site_data[0]['h1']})
        else:
            print "not changed"

        # check get_sites_description

        if str(last_record[0]['meta_description']) != str(site_data[0]['meta_description']):
            print 'changed'
            send_mail("Current description is {0} on {1}".format(site_data[0]['meta_description'], url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "4",
                                                     "data": "Current description %s" % site_data[0]['meta_description']})
        else:
            print "not changed"

        # check get_sites_sitemap

        if str(last_record[0]['sitemap']) != str(site_data[0]['sitemap']):
            print 'changed'
            send_mail("Current sitemap changed on {0}".format(url))
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "7",
                                                     "data": "Current sitemap changed"})
        else:
            print "not changed"

        # check get_sites_html

        if str(last_record[0]['html']) != str(site_data[0]['html']):
            print 'changed'
            send_mail("Current html changed on %s" % url)
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "8",
                                                     "data": "Current html changed"})
        else:
            print "not changed"

        # check ip

        if str(last_record[0]['ip']) != str(site_data[0]['ip']):
            print 'changed'
            send_mail("Current ip changed on %s" % url)
            status = Statuses(Wrapper()).add_status({"site_id": id, "status_id": "2",
                                                     "date": curdatetime, "type_id": "8",
                                                     "data": "Current ip changed for %s" % site_data[0]['ip']})
        else:
            print "not changed"

        if add_site_data == "-1":
            return "Error.Try again"
        return "check done"


@app.route('/test1')
def test1():
    id = 116
    last_record = SiteData(Wrapper()).get_last_record(id)
    return last_record[0]['title']


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
else:
    logging.basicConfig(debug=True, threaded=True,
                        host='0.0.0.0', port=5000)





