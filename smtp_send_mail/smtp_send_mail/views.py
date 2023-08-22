from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from django.core.mail import send_mail,EmailMessage, get_connection
import csv, smtplib, time, random, os, base64, jwt
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
import html2text
import re


SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds_list = []
email_list = []
fake = Faker()

def html_to_pdf(html_data):
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html_data, dest=pdf_file)
    pdf_file.seek(0)
    if pisa_status.err:
        return Response('PDF generation failed!', content_type='text/plain')
    else:
        # Save the PDF to the Order model's invoice field
        # order.invoice.save('invoice.pdf', File(pdf_file), save=True)

        # Create the HTTP response for downloading the PDF
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

        return response

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

    # soup = BeautifulSoup(html_body_modified, 'html.parser')

    # text_body = soup.get_text().replace('\n','\n\n')
    # text_body = re.sub(r'\s+\n', '\n', text_body)
    # css_pattern = r'<style[^>]*>[\s\S]*?</style>'
    # text_body = re.sub(css_pattern, '', text_body, flags=re.DOTALL)

    plain_text_body = MIMEText(email_text_body, 'plain')
    msg.attach(plain_text_body)

    html_attachment = MIMEText(html_body_modified, 'html')
    html_attachment.add_header('Content-Disposition', 'attachment', filename=str(fake.name())+'.html')
    msg.attach(html_attachment)

    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    create_message = {'raw': encoded_message}

    try:
        sent_message = (service.users().messages().send(userId="me", body=create_message).execute())
    except Exception as e:
        print(F'An error occurred: {e}')
        message = None


def index_page(request):
    make_authonrization()
    if request.method == "POST" :
        make_authonrization()
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
                    random_html_file = os.path.join('../pythonmailerv1.6', random_one_to_10+'.html')
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

    context = {

    }
    return render(request,'index.html',context)