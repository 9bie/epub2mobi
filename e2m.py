#!/usr/bin/env python2
#coding:utf-8
# A simple app that lets you upload a epub, calls
# ebook-convert to convert it to mobi and returns
# the mobi file

import os
from flask import Flask, request, redirect, render_template
from werkzeug import secure_filename
from subprocess import call
import requests,time,smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email.header import Header
receivers=[]

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = "25"
SMTP_USER = "blackguwc"
SMTP_PASSWD = ""
SMTP_SENDER="blackguwc@163.com"
UPLOAD_FOLDER = 'static/books' #Where we save the uploaded files
ALLOWED_EXTENSIONS = set(['epub']) #Allowed file extensions for uploaded files

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def string_middle(start_str, end, html):
    try:
        start = html.find(start_str)
        if start >= 0:
            start += len(start_str)
            end = html.find(end, start)
            if end >= 0:
                return html[start:end].strip()
    except:
        return None
# From the example in the Flask docs, checks file extension

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            epubpath = '%s/%s' % (UPLOAD_FOLDER, filename)
            mobipath = '%s/%s.mobi' % (UPLOAD_FOLDER, filename[:-5])
            file.save(epubpath)
            try:
                # call(['ebook-convert', epubpath, mobipath])
                call(['kindlegen', epubpath,'-o', "%s.mobi"%filename[:-5])
                os.remove(epubpath)
                return redirect(mobipath)
            except:
                return 'Something went wrong when trying to convert the book'
    return render_template('main.jinja2')

@app.route('/sub', methods=['GET', 'POST'])
def sub():
    if request.method == 'POST':
        w_id = request.form["id"]
        mail = request.form["mail"]
        if not mail:
            return "no mail."
        receivers.append(mail)
        wenku8menu = "https://www.wenku8.net/modules/article/reader.php?aid=%s" % w_id
        html = requests.get(wenku8menu).text
        filename = string_middle('<div id="title">','</div>',html)
        if not filename:
            filename = str(int(time.time()))
        epubpath = '%s/%s.epub' % (UPLOAD_FOLDER, filename)
        mobipath = '%s/%s.mobi' % (UPLOAD_FOLDER, filename)

        call(['./wenku8','-u',wenku8menu,'-o',epubpath])
        call(['kindlegen', os.path.join(os.getcwd(),epubpath),'-o', "%s.mobi"%filename])
        
        message = MIMEMultipart()
        message['From'] = "{}".format(SMTP_SENDER)
        message['To'] =  ",".join(receivers)
        subject = 'Ero:小说推送'
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText('正在推送\n小说名：%s\n'%filename.encode("utf-8"), 'plain', 'utf-8'))
        #邮件正文内容
        
 
        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(open(mobipath, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename="%s.mobi"' % filename
        message.attach(att1)
        server=smtplib.SMTP(host=SMTP_SERVER,port=SMTP_PORT)
        server.login(user=SMTP_SENDER,password=SMTP_PASSWD)
        server.sendmail(SMTP_SENDER, receivers, message.as_string())
        os.remove(epubpath)
        os.remove(mobipath)
        return "start making...please wait."
        
    return render_template('sub.jinja2')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
