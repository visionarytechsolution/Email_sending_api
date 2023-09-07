from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.core.mail import send_mail,EmailMessage, get_connection
from django.http import JsonResponse, StreamingHttpResponse
import csv, smtplib, time, random, os, base64, re, string, time
from faker import Faker
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from email.mime.application import MIMEApplication
from weasyprint import HTML
from email.utils import formataddr
import pdfkit
import asyncio
import json
import threading, re
import logging

logger = logging.getLogger(__name__)



SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds_list = []
email_list = []
failed_email_list = []
rcver_failed_email_list = []
unique_list = []
success_email_list = []
fake = Faker()


def get_user_email(creds):
    id_token = creds.id_token
    email = decode_id_token(id_token).get('email')
    return email

def decode_id_token(id_token):
    return id_token.verify_oauth2_token(id_token, Request())

def make_authonrization():
    for filename in os.listdir('../pythonmailerv1.6/creds'):
        if filename.endswith('.json'):
            next = True
            try:
                creds = Credentials.from_authorized_user_file(os.path.join('../pythonmailerv1.6/creds', filename), scopes=SCOPES)
                creds_list.append(creds)
                email_list.append(filename)
                next = False
            except Exception as e:
                print("Error loading credentials 1:", e)
            if next:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(os.path.join('../pythonmailerv1.6/creds', filename), SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(os.path.join('../pythonmailerv1.6/creds', filename), 'w') as token:
                        token.write(creds.to_json())
                    email_list.append(filename)
                except Exception as e:
                    print("Error loading credentials 2:", e)    


def read_html_file(file_path):
    with open(file_path, 'r') as file:
        html_string = file.read()
    return html_string



def send_mail_func(subject, message, recipient_list, random_html_file, html_body_modified, email_text_body):

    make_authonrization()

    timestamp = int(time.time())
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    invoice_id = f'INV{timestamp}_{random_chars}'

    length_creds = len(creds_list)


    for i in range(len(creds_list)):

        random_name = fake.name()
        random_index = random.randrange(len(creds_list))
        sender_creds = creds_list[random_index]
        from_email_catch = email_list[random_index]
        from_email_send = from_email_catch.split('.json')[0]

        service = build('gmail', 'v1', credentials=sender_creds)

        msg = MIMEMultipart()
        msg['to'] = ', '.join(recipient_list) 
        msg['subject'] = subject
        sender_formatted = formataddr((random_name, from_email_send))
        msg['From'] = sender_formatted


        plain_text_body = MIMEText(email_text_body, 'plain')
        msg.attach(plain_text_body)

        # pdf_data = HTML(string=html_body_modified).write_pdf()
        config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdf_data = pdfkit.from_string(html_body_modified, False, configuration=config, options={"enable-local-file-access": ""})


        html_attachment = MIMEApplication(pdf_data, _subtype='pdf')
        html_attachment.add_header('Content-Disposition', 'attachment', filename=str(invoice_id)+'.pdf')
        msg.attach(html_attachment)

        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        create_message = {'raw': encoded_message}

        try:
            sent_message = (service.users().messages().send(userId="me", body=create_message).execute())
            time.sleep(3)
            break
        except Exception as e:
            creds_list.pop(random_index)
            print(i)
            if i == len(creds_list):
                failed_email_list.append(from_email_send)
                rcver_failed_email_list.append(recipient_list)
                print(F'An error occurred: {e}  from {from_email_send}')
            message = None


def index_page(request):
    failed_email_list.clear()
    rcver_failed_email_list.clear()
    if request.method == "POST" :
        try:
            subject_file = request.FILES['subject_file']
            # sender_email_conf = request.FILES['sender_email_conf']
            rcvr_emails = request.FILES['rcvr_emails']
            # html_body = request.FILES['html_body']
            html_body_content = request.FILES['html_body_content']

            #subject file read and print
            lines = subject_file.readlines()
            subject_file_data = random.choice(lines)
            subject_file_data = subject_file_data.decode("utf-8").strip().strip('\"')
            # print(subject_file_data) #show file data in console


            #rcvr mail read from file
            rcvr_mail_file_data=pd.read_excel(rcvr_emails,engine='openpyxl')
            # print(rcvr_mail_file_data['Email'][0]) #show file data in console
            rcvr_email_list = []
            for i in range(len(rcvr_mail_file_data)):
                rcvr_email_list.append(rcvr_mail_file_data['Email'][i])
            # rcvr_order_numbers_list = rcvr_mail_file_data['Order Number']


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
            email_body = mail_body_file_data['Body']

            if len(u_email_list) == len(rcvr_email_list):
                for each_item in range(len(rcvr_email_list)):
                    if (each_item + 1) % 10 == 0:
                        time.sleep(10)
                    #email body read from html
                    random_one_to_10 = str(random.randint(1,10))
                    random_html_file = os.path.join('../pythonmailerv1.6', '11'+'.html')
                    text_body = f'Hello {str(f_name_list[each_item])}\n{str(u_email_list[each_item])}\n{str(random.randint(99999,99999999999))}\n{str(email_body[each_item])}'
                    with open(random_html_file, 'r') as html_body:
                        html_body_file_data = html_body.read()

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

                        
                        send_mail_func(subject_file_data,html_body_file_data,[rcvr_email_list[each_item]], random_html_file, html_body_file_data, text_body)
                messages.info(request, "File uploaded successfully !!!")
            else:
                messages.error(request, "Receiver Email and Email Body content file data count is not matching!!!")

        except Exception as e:
            messages.error(request,str(e))
        print("Sender failed email list:")
        unique_list = list(set(failed_email_list))
        print(unique_list)
        print("Receiver failed email list:")
        print(rcver_failed_email_list)

    context = {

    }
    return render(request,'index.html',context)



def send_mail_func2(subject, recipient_list, html_body_modified, email_text_body, proxy_info):
    
    make_authonrization()

    timestamp = int(time.time())
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    invoice_id = f'INV{timestamp}_{random_chars}'

    length_creds = len(creds_list)

    x = 0


    for i in range(len(creds_list)):

        try:
            host = proxy_info[x]['host']
            port = proxy_info[x]['port']

            session = requests.Session()
            session.proxies = {
                "http": host + ':' + str(port),
                "https": host + ':' + str(port)
            }
            x = x + 1
        except Exception as e:
            x = x + 1
            message = f"<span class='text-danger'>Proxy ip error for {host}:{port}</span>"

        random_name = fake.name()
        random_name = str(random.randint(9999,999999)) + ' ' + random_name
        random_index = random.randrange(len(creds_list))
        sender_creds = creds_list[random_index]
        from_email_catch = email_list[random_index]
        from_email_send = from_email_catch.split('.json')[0]

        service = build('gmail', 'v1', credentials=sender_creds)


        msg = MIMEMultipart()
        msg['to'] = recipient_list
        msg['subject'] = f"{subject}"
        sender_formatted = formataddr((random_name, from_email_send))
        msg['From'] = sender_formatted


        plain_text_body = MIMEText(email_text_body, 'plain')
        msg.attach(plain_text_body)

        if os.name == "posix":
            pdf_data = HTML(string=html_body_modified).write_pdf()
        else:
            config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
            pdf_data = pdfkit.from_string(html_body_modified, False, configuration=config, options={"enable-local-file-access": ""})


        html_attachment = MIMEApplication(pdf_data, _subtype='pdf')
        html_attachment.add_header('Content-Disposition', 'attachment', filename=str(invoice_id)+'.pdf')
        msg.attach(html_attachment)

        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        create_message = {'raw': encoded_message}



        try:
            sent_message = (service.users().messages().send(userId="me", body=create_message).execute())
            if sent_message:
                success_email_list.append(recipient_list)
                message = f"<span class='text-success'>Successfully sent to {recipient_list}</span>"
                break
        except Exception as e:
            creds_list.remove(sender_creds)
            if i == len(creds_list):
                failed_email_list.append(from_email_send)
                rcver_failed_email_list.append(recipient_list)
                message = f"<span class='text-danger'>Failed to sent {recipient_list}</span>"

    return message
        
stop_flag = False

@csrf_exempt
def home_page(request):
    if request.method == 'POST':

        creds_list.clear()
        email_list.clear()
        success_email_list.clear()
        failed_email_list.clear()
        rcver_failed_email_list.clear()

        def generate_updates():
            receiver_data_file = request.FILES.get('receiverData')
            json_data_files = request.FILES.getlist('jsonData')
            ip_file = request.FILES.get('ipfile')
            speed_control_str = request.POST.get('speedControl', '')

            if speed_control_str.isdigit():
                speed_control = int(speed_control_str)
            else:
                speed_control = 1

            # subject
            is_file_or_text = request.POST.get('isFileOrText')
            subject = None
            hash_tags = []
            if is_file_or_text:
                if is_file_or_text == 'on':
                    subject_file = request.FILES.get('subjectFile')
                    if subject_file:
                        lines = subject_file.readlines()
                        subject_file_data = random.choice(lines)
                        subject = subject_file_data.decode("utf-8").strip().strip('\"')
            else:
                subject = str(request.POST.get('subject'))    
                pattern = r'#([^ ]+)'
                matches = re.findall(pattern, subject)

                for match in matches:   
                    if match == 'randomNumber':
                        subject = subject.replace('#randomNumber', str(random.randint(99999, 99999999)))
                    elif match == 'randomInvoice':
                        rand_inv = 'INVOICE_' + str(random.randint(9999, 99999))
                        subject = subject.replace('#randomInvoice', rand_inv)
                    else:
                        hash_tags.append(match)  


            # email content body
            content_body = None
            is_file_or_text2 = request.POST.get('isFileOrText2')
            body_hash_tag = []
            if is_file_or_text2:
                if is_file_or_text2 == 'on':
                    body_file = request.FILES.get('bodyFile')
                    if body_file:
                        lines = body_file.readlines()
                        body_file_data = random.choice(lines)
                        content_body = subject_file_data.decode("utf-8").strip().strip('\"')                        
            else:
                content_body = request.POST.get('contentBody')
                pattern = r'#([^ ]+)'
                matches = re.findall(pattern, content_body)

                for match in matches:   
                    if match == 'randomNumber':
                        content_body = content_body.replace('#randomNumber', str(random.randint(99999, 99999999)))
                    elif match == 'randomInvoice':
                        rand_inv = 'INVOICE_' + str(random.randint(9999, 99999))
                        content_body = content_body.replace('#randomInvoice', rand_inv)
                    else:
                        body_hash_tag.append(match)  

                
            # remove existing credentials
            parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
            creds_dir = os.path.join(parent_directory, 'pythonmailerv1.6', 'creds')
            if not os.path.exists(creds_dir):
                os.makedirs(creds_dir)
            for filename in os.listdir(creds_dir):
                if filename.endswith('.json'):
                    os.remove(creds_dir + '/' + filename)


            # validation check
            can_start = True
            if subject == "" or subject is None:
                can_start = False
                yield b"<span class='text-danger'>Subject not found</span>\n"

            if content_body == "" or content_body is None:
                can_start = False
                yield f"<span class='text-danger'>Email body content not found!\n"

            if not json_data_files:
                can_start = False
                yield f"<span class='text-danger'>JSON Credentials file not found</span>\n"
            else:
                try:
                    for json_file in json_data_files:
                        fs = FileSystemStorage(location=os.path.join('../pythonmailerv1.6/creds'))
                        fs.save(json_file.name, json_file)
                except Exception as e:
                    can_start = False
                    yield f"<span class='text-success'>For JSON file: {e}</span>\n"
                    print(f'For JSON file: {e}')

            proxy_info = None
            if not ip_file:
                can_start = False
                yield f"<span class='text-danger'>Ip rotation file not found!\n"
            else:
                try:
                    df = pd.read_csv(ip_file)
                    proxy_info = df.to_dict(orient='records')
                except Exception as e:
                    can_start = False
                    yield f'<span class="text-danger">For ip rotation file: {e}</span>\n'

            if not receiver_data_file:
                can_start = False
                yield f'<span class="text-danger">Receiver file not found</span>\n'


            if can_start == True:  
                try:
                    df = pd.read_excel(receiver_data_file)
                    receiver_data_content = df.to_dict(orient='records')
                    
                    random_one_to_10 = str(random.randint(1,10))
                    random_html_file = os.path.join('../pythonmailerv1.6', str('11'+'.html'))

                    seen_data = set()

                    for data in receiver_data_content:

                        global stop_flag
                        if stop_flag:
                            break

                        for tag in hash_tags:
                            formated_tag = str(tag.replace('_', ' '))
                            subject = subject.replace('#'+tag, str(data[formated_tag]))

                        for tag in body_hash_tag:
                            formated_tag = str(tag.replace('_', ' '))
                            content_body = content_body.replace('#'+tag, str(data[formated_tag]))

                        email_receiver = data['Email']

                        with open(random_html_file, 'r') as html_body:
                            html_body_file_data = html_body.read()

                            html_body_file_data = html_body_file_data.replace("{f_name}",str(data['F Name']))
                            html_body_file_data = html_body_file_data.replace("{tag}",str(data['Tag']))
                            html_body_file_data = html_body_file_data.replace("{id1}",str(data['Id1']))
                            html_body_file_data = html_body_file_data.replace("{id2}",str(data['Id2']))
                            html_body_file_data = html_body_file_data.replace("{id3}",str(data['Id3']))
                            html_body_file_data = html_body_file_data.replace("{id4}",str(data['Id4']))
                            html_body_file_data = html_body_file_data.replace("{year}",str(data['Year']))
                            html_body_file_data = html_body_file_data.replace("{item}",str(data['Item']))
                            html_body_file_data = html_body_file_data.replace("{today_date}",str(data['Date2']))
                            html_body_file_data = html_body_file_data.replace("{date2}",str(data['Date2']))
                            html_body_file_data = html_body_file_data.replace("{phone}",str(data['Phone']))
                            html_body_file_data = html_body_file_data.replace("{amount}",str(data['Amount']))
                            html_body_file_data = html_body_file_data.replace("{u_name}",str(data['U Name']))
                            html_body_file_data = html_body_file_data.replace("{u_email}",str(data['U Email']))
                            html_body_file_data = html_body_file_data.replace("{company}",str(data['Company']))

                            res = send_mail_func2(subject, email_receiver, html_body_file_data, content_body, proxy_info)
                            msg =  f"Message: {res}"
                            
                            if msg not in seen_data:
                                seen_data.add(msg)
                                yield msg + '\n'

                            time.sleep(int(speed_control))
                    
                    messages.info(request, "File uploaded successfully !!!")
                    
                except Exception as e:
                    logger.exception(str(e))
                    yield f"<span class='text-danger'>Receiver file: {e}</span>\n"
                    messages.error(request, e)
            else:
                return

            # print("Sender failed email list:")
            # unique_list = list(set(failed_email_list))
            # print(unique_list)
            # print("Receiver failed email list:")
            print(' '.join(list(set(rcver_failed_email_list))))
            yield f"<span class='text-success'>{str(len(success_email_list))} mail sent successfully</span>\n"
            yield f"<span class='text-danger'>Json failed emails:</span> {' '.join(list(set(failed_email_list)))}\n"
            yield f"<span class='text-danger'>Receiver failed email list:</span> {' '.join(list(set(rcver_failed_email_list)))}\n"


        response = StreamingHttpResponse(generate_updates(), content_type='text/plain')
        response['Cache-Control'] = 'no-cache'
        response['Content-Disposition'] = 'inline; filename="output.txt"'
        return response



    return render(request, 'home.html')


def stop_generator(request):
    global stop_flag
    stop_flag = True
    return JsonResponse({"message": "Program stopped"})