import os 
import re 
import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def helper_total_processed(subject, server, email):
    msg = MIMEMultipart()
    msg['From'] = os.environ.get('email_from')
    msg['To'] = email
    msg['Subject'] = subject
    text = msg.as_string()     
    server.sendmail('CRMUpdate@gpwa.com', email, text)     
    server.quit()    

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
    


if __name__ == '__main__':    
    uploaded_to_autopop(f"Uploaded to Autopopulate",  3)
    bankname = 'test'
    month = 'test'
    year = 'test'
    count = 10
    uploaded_to_flexi('tkorpal@gpwa.com', f"{bankname} {month} {year}", count)