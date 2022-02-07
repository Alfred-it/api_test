#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import smtplib
import sys,os
sys.path.append('../')

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def sendmail(msgg, files):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 由于没有 autotest@xylink.com 邮箱，暂先使用该qaredmine邮箱，如有必要，后续可以根据需要替换 ---haochuang
    mail_host = "smtp.exmail.qq.com"
    mail_user = "jiajinhang@xylink.com"
    mail_pass = "2458624684Aa"
    rec_user = "jingjunwei@xylink.com,zhouyu@xylink.com,jiajinhang@xylink.com"
    # rec_user = "jiajinhang@xylink.com"
    subject = "API自动化测试报告-PRE-" + time
    print(rec_user)
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mail_user
    msg['To'] = rec_user
    msg.attach(MIMEText(msgg, _subtype='html', _charset='utf-8'))
    for file in files:
        print(file)
        html = MIMEApplication(open(file, 'rb').read())
        html.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
        msg.attach(html)

    try:
        server = smtplib.SMTP_SSL(mail_host)
        server.connect(mail_host,465)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, rec_user.split(','), msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)