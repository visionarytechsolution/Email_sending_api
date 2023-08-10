from django.shortcuts import render
from django.contrib import messages
import random
import pandas as pd

def read_html_file(file_path):
    with open(file_path, 'r') as file:
        html_string = file.read()
    return html_string

def index_page(request):
    if request.method == "POST" :
        try:
            subject_file = request.FILES['subject_file']
            sender_email_conf = request.FILES['sender_email_conf']
            rcvr_emails = request.FILES['rcvr_emails']
            html_body = request.FILES['html_body']
            # html_body_content = request.FILES['html_body_content']

            #subject file read and print
            subject_file_data = subject_file.read()
            # print(subject_file_data) #show file data in console

            #sender file read and print
            sender_mail_file_data=pd.read_excel(sender_email_conf,engine='openpyxl')
            # print(sender_mail_file_data) #show file data in console
            sender_email = ['Email'][0]
            sender_password = ['Password'][0]
            sender_server = ['Server'][0]
            sender_port = ['Port'][0]


            #rcvr mail read from file
            rcvr_mail_file_data=pd.read_excel(rcvr_emails,engine='openpyxl')
            # print(rcvr_mail_file_data) #show file data in console
            rcvr_email_list = rcvr_mail_file_data['Email']
            rcvr_order_numbers_list = rcvr_mail_file_data['Order Number']


            #email body read from html
            html_body_file_data = html_body.read().decode()
            # print(html_body_file_data) #show file data in console


            messages.info(request,"File uploaded successfully !!!")
        except Exception as e:
            messages.error(request,str(e))

    context = {

    }
    return render(request,'index.html',context)