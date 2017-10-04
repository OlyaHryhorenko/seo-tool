import json
import os
import imghdr
import hashlib
import datetime, time
from datetime import datetime, timedelta
from datetime import date
from werkzeug.utils import secure_filename
from smtplib import SMTP_SSL, SMTP
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_mail import Mail
from flask_mail import Message
from apps.models.decorators import async

site_mail = 'support@pro-essay-writer.com'
mail = Mail()

def delta_date(date1, date2):
    date_format = "%Y-%m-%d"
    delta = datetime.strptime(date1, date_format) - datetime.strptime(date2, date_format)
    return delta.days
    
def get_dict(multi_dict):
    return json.loads(json.dumps(multi_dict, separators=(',', ':')))


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    """ Check image by file extension
        Get filename and check in ALLOWED_EXTENSIONS
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_image(filename):
    """ Check image format
        Checking whether a file is a picture use imghdr.what - return file type if a picture or None
    """
    img_type = imghdr.what(filename)
    if img_type != None and any(img_type in s for s in ALLOWED_EXTENSIONS):
        return True
    else:
        return False


def upload():
    """Upload pictures to the server
        Get data from picture upload forrm and upload image
    """
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            hash = hashlib.sha1()
            # Hash to guarantee uniqueness file name
            hash.update(str(time.time()))
            filename = os.path.join(
                app.config['UPLOAD_FOLDER'], hash.hexdigest()[:10] + secure_filename(file.filename))
            file.save(filename)
            if check_image(filename):
                return 'ok'
            else:
                os.remove(filename)  # remove picture if file not valid
                return 'no image'
        else:
            return 'type error'


def is_pwd(passwd):
        """ Check pwd hash a-f0-9 len 128 """
        result = None
        try:
            result = re.match('^[a-f0-9]{128}$', passwd).group(0)
        except:
            pass
        return result is not None


def is_email(email):
        """ Check mail """
        result = None
        try:
            result = re.match(
                '^[_A-Za-z0-9-+]+(.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(.[A-Za-z0-9]+)*(.[A-Za-z]{2,})$', email).group(0)
        except:
            pass
        return result is not None


def is_username(uname):
        """ check username """
        result = None
        try:
            result = re.match('^[a-zA-Z0-9_\.+-@#]{3,28}$', uname).group(0)
        except:
            pass
        return result is not None


def is_number(num):
        """ Check is number"""
        try:
            long(num)
        except ValueError:
            return False
        return True

def send_mail(login, password, from_address ,to_address, subject, text, html):
    # Compose message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    if (text != ""):
        text = text
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)

    if (html != ""):    
        html = html
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

    # Send mail
    smtp = SMTP()
    smtp.connect("mbxsrv.com")
    smtp.login(login, password)
    smtp.sendmail(from_address, to_address, msg.as_string())
    ###print "login : {0}".format(login)
    ###print "password : {0}".format(password)
    ###print "from_address : {0}".format(from_address)
    ###print "to_address : {0}".format(to_address)
    ###print "subject : {0}".format(subject)
    ###print "text : {0}".format(text)
    ###print "html : {0}".format(html)
    smtp.quit()

def send_mail_from_server(subject, to_address, body, html):
    msg = Message(subject, sender=site_mail, recipients=[to_address])
    msg.body = body
    msg.html = html
    mail.send(msg)

def GetListFile(path_to_find='templates',end_width=".html",execute_path="adm_template/"):
    list_file=[]
    path_to_find_long="{}".format(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../{}".format(path_to_find))))
    ###print "{}".format(path_to_find_long)
    for dirpath, dirnames, filenames in os.walk(path_to_find_long):
        ###print dirpath
        ###print dirnames
        ###print filenames
        for filename in [f for f in filenames if f.endswith(end_width)]:
            pth=str(os.path.join(dirpath, filename)).replace(path_to_find_long,"")
            if (pth.find(execute_path) < 0):
                list_file.append(pth)
    return list_file

def convert_pp_response_to_dict(pp_response):
    if pp_response is None:
        return None
    try:
        pp_dict_resp = {}
        keys_map = {"PAYMENTREQUEST_0_CUSTOM": "UID_CUSTOMER",
                    "PAYMENTREQUEST_0_INVNUM": "UID_CUSTOMER",
                    "PAYMENTREQUESTINFO_0_TRANSACTIONID": "TRANSACTIONID_CUSTOMER",
                    "PAYMENTREQUEST_0_TRANSACTIONID": "TRANSACTIONID_CUSTOMER",
                    "TRANSACTIONID": "TRANSACTIONID_CUSTOMER",
                    "PAYMENTREQUEST_0_NOTETEXT": "NOTETEXT_CUSTOMER",
                    "NOTETEXT": "NOTETEXT_CUSTOMER"}
        for k, v in pp_response.items():
            if keys_map.get(k):
                pp_dict_resp[keys_map[k]] = v
                continue
            pp_dict_resp[k] = v
        if "NOTETEXT_CUSTOMER" not in pp_dict_resp:
            pp_dict_resp["NOTETEXT_CUSTOMER"] = "0.0.0.0"
        return pp_dict_resp
    except Exception as e:
        SendMessageToBot().sent_text_to_telegram("[e] convert_pp_response_to_dict - {}".format(e))
        return None

