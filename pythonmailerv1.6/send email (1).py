#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time


import socks

#socks.setdefaultproxy(TYPE, ADDR, PORT)
# socks.setdefaultproxy(socks.SOCKS5, 'proxy.proxy.com', 8080)
# socks.wrapmodule(smtplib)

# In[42]:


subject=input("Enter Subject: \n")
html_content = input("Enter Html of the Body:\n")
t=int(input("Enter The Time Delay in Secounds: "))

# In[ ]:





# In[43]:


mails=pd.read_excel('smtp.xlsx')
users = pd.read_excel('book1.xlsx')


# In[ ]:





# In[44]:



def read_html_file(file_path):
    with open(file_path, 'r') as file:
        html_string = file.read()
    return html_string


# Function to send email with attachments
def send_email(recipient,first_name,last_name,order_number,sender,password):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = sender
    smtp_password = password
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    head=subject
    head=head.replace('{First Name}', first_name)
    head=head.replace('{Last Name}', last_name)
    head=head.replace('{Order Number}', str(order_number))

    msg['Subject'] = head
    body=html_content
    body=body.replace('{First Name}', first_name)
    body=body.replace('{Last Name}', last_name)
    body=body.replace('{Order Number}', str(order_number))

    html_string = read_html_file("{}.html".format(html_content))
    html_string=html_string.replace('{f_name}',first_name+' '+last_name)
    
    msg.attach(MIMEText(html_string, 'html'))




    try:
        server = smtplib.SMTP(smtp_server,smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        # server.sendmail(sender, recipient, html_string)
        print(f"Email sent to {recipient}")
        server.quit()
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
    time.sleep(t)
# Read data from Excel file using pandas DataFrame


# In[45]:


i=0
while i<len(users):
    send_email(users["Email"][i],users['First Name'][i],users['Last Name'][i],users['Order Number'][i],mails['Email'][i%len(mails)],mails['Password'][i%len(mails)])
    i=i+1


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




