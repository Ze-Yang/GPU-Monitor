# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
import socket
import time
from email.mime.text import MIMEText

# third-party SMTP service
mail_host = "smtp.xxx.com"  # set SMTP server
mail_user = "xxx@xxx.com"  # sender username
mail_pass = "xxx"  # password
receivers = ['xxx@xxx.com']  # receivers


def send_mail(cmd, finish=False, time_used=None, subject=None, content=None):
    sender = "GPU monitor" + "<" + mail_user + ">"

    if subject is None:
        if finish:
            subject = 'Task Finished Notification'
        else:
            subject = 'Task Starting Notification'
    if content is None:
        tm = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        hostname = socket.gethostname()
        if finish:
            m, s = divmod(time_used, 60)
            h, m = divmod(m, 60)
            msg = f'Your task running with the following command finished in {h:.0f} h {m:.0f} m {s:.0f} s.\n\n'
        else:
            msg = f'Your task started running at {tm} with the following command.\n\n'
        content = 'Hi,\n\n' + msg + cmd + \
                  '\n\nThis is a system generated email, do not reply.\n\n' \
                  'Nice day,\n' + hostname
        print(content)
    message = MIMEText(content)
    message['From'] = sender
    message['To'] = ';'.join(receivers)
    message['Subject'] = subject

    try:
        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(mail_host, port=25)  # SMTP default port 25
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, receivers, message.as_string())
        print("Message sent successfully.")
    except smtplib.SMTPException:
        print("Error: fail to send the message.")
    else:
        return
