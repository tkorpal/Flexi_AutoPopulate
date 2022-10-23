import os 
import re 
import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def email_total_processed(processname, status, email):
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(os.environ.get('email_host'), os.environ.get('email_port'))
        server.starttls(context=context)
        server.login(os.environ.get('email_from'), os.environ.get('email_pwd'))
    except Exception as error:
        pass 
    finally:
        subject = f'{processname} ---- Total Processed: {status}'
        helper_total_processed(subject, server, email)

def flexi_email(processname, status, email):
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(os.environ.get('email_host'), os.environ.get('email_port'))
        server.starttls(context=context)
        server.login(os.environ.get('email_from'), os.environ.get('email_pwd'))
    except Exception as error:
        pass 
    finally:
        subject = f'{processname} ---- Uploaded to FlexiCapture: {status}'
        helper_total_processed(subject, server, email)
    
        
def uploaded_to_flexi(email, processname, count):
    total = lambda x, y : True if x == 0 else flexi_email(f"{processname} {y}", x, email)
    total(count,'')


def uploaded_to_autopop(processname, count):   
    total = lambda x, y : True if x == 0 else email_total_processed(f"{processname} {y}", x, 'tkorpal@gpwa.com')
    total(count,'')