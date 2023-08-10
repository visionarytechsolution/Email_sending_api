from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from django.core.mail import send_mail,EmailMessage,get_connection

def read_html_file(file_path):
    with open(file_path, 'r') as file:
        html_string = file.read()
    return html_string

def send_mail_func(subject,message,email_from,sender_password,recipient_list):
    # print(subject,message,email_from,recipient_list)
    try:
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=email_from,
            password=sender_password
        )
        email = EmailMessage(
            subject,
            message,
            email_from,
            recipient_list,
            [],
            reply_to=[],
            # headers={'Message-ID': 'foo'},
            connection=connection
        )
        # email.attach_file(attachment_path + 'attachment.pdf')
        email.content_subtype = 'html'
        email.send()
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
            subject_file_data = subject_file.readline()
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
            amount_list = mail_body_file_data['Amount']

            if len(u_email_list) == len(rcvr_email_list):
                for each_item in range(len(rcvr_email_list)):
                    html_body_file_data = html_body_file_data.replace("{f_name}",str(f_name_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{tag}",str(tag_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{id1}",str(id1_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{id2}",str(id2_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{id3}",str(id3_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{id4}",str(id4_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{year}",str(year_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{item}",str(item_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{today_date}",str(date2_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{date2}",str(date2_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{phone}",str(phone_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{amount}",str(amount_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{u_name}",str(u_name_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{u_email}",str(u_email_list[each_item]))
                    html_body_file_data = html_body_file_data.replace("{company}",str(company_list[each_item]))

                    send_mail_func(subject_file_data,html_body_file_data,sender_email,sender_password,[rcvr_email_list[each_item]])
                messages.info(request, "File uploaded successfully !!!")
            else:
                messages.error(request, "Receiver Email and Email Body content file data count is not matching!!!")



        except Exception as e:
            messages.error(request,str(e))

    context = {

    }
    return render(request,'index.html',context)