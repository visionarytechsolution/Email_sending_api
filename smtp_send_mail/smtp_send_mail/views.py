from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from django.core.mail import send_mail


def read_html_file(file_path):
    with open(file_path, 'r') as file:
        html_string = file.read()
    return html_string

def send_mail_func(subject,message,email_from,sender_password,recipient_list):
    # print(subject,message,email_from,recipient_list)
    try:
        send_mail(
            subject,
            message,
            email_from,
            recipient_list,
            auth_user=email_from,
            auth_password = sender_password,
            fail_silently=False,
        )
    except Exception as e:
        print("email error: "+str(e))

def index_page(request):
    if request.method == "POST" :
        try:
            subject_file = request.FILES['subject_file']
            sender_email_conf = request.FILES['sender_email_conf']
            rcvr_emails = request.FILES['rcvr_emails']
            html_body = request.FILES['html_body']
            html_body_content = request.FILES['html_body_content']

            #subject file read and print
            subject_file_data = subject_file.read()
            # print(subject_file_data) #show file data in console

            #sender file read and print
            sender_mail_file_data=pd.read_excel(sender_email_conf,engine='openpyxl')
            # print(sender_mail_file_data) #show file data in console
            sender_email = sender_mail_file_data['Email'][0]
            sender_password = sender_mail_file_data['Password'][0]
            sender_server = sender_mail_file_data['Server'][0]
            sender_port = sender_mail_file_data['Port'][0]


            #rcvr mail read from file
            rcvr_mail_file_data=pd.read_excel(rcvr_emails,engine='openpyxl')
            # print(rcvr_mail_file_data['Email'][0]) #show file data in console
            rcvr_email_list = []
            for i in range(len(rcvr_mail_file_data)):
                rcvr_email_list.append(rcvr_mail_file_data['Email'][i])
            # rcvr_order_numbers_list = rcvr_mail_file_data['Order Number']


            #email body read from html
            html_body_file_data = html_body.read().decode()
            # print(html_body_file_data) #show file data in console

            #email body data read from file
            mail_body_file_data=pd.read_excel(html_body_content,engine='openpyxl')
            # print(mail_body_file_data) #show file data in console
            f_name_list = mail_body_file_data['F Name']
            company_list = mail_body_file_data['Company']
            date2_list = mail_body_file_data['Date2']
            year_list = mail_body_file_data['Year']
            phone_list = mail_body_file_data['Phone']
            tag_list = mail_body_file_data['Tag']
            id4_list = mail_body_file_data['Id4']
            id2_list = mail_body_file_data['Id2']
            id1_list = mail_body_file_data['Id1']
            id3_list = mail_body_file_data['Id3']
            item_list = mail_body_file_data['Item']
            u_name_list = mail_body_file_data['U Name']
            u_email_list = mail_body_file_data['U Email']

            if len(u_email_list) == len(rcvr_email_list):
                send_mail_func("abc",html_body_file_data,sender_email,sender_password,rcvr_email_list)
                messages.info(request, "File uploaded successfully !!!")
            else:
                messages.error(request, "Receiver Email and Email Body content file data count is not matching!!!")



        except Exception as e:
            messages.error(request,str(e))

    context = {

    }
    return render(request,'index.html',context)