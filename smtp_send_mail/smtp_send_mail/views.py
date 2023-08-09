from django.shortcuts import render
from django.contrib import messages
def index_page(request):
    if request.method == "POST" :
        try:
            subject_file = request.FILES['subject_file']
            # sender_email_conf = request.FILES['sender_email_conf']
            # rcvr_emails = request.FILES['rcvr_emails']
            # html_body = request.FILES['html_body']
            # html_body_content = request.FILES['html_body_content']

            subject_file_data = subject_file.readline()
            print(subject_file_data)
            messages.info(request,"File uploaded successfully !!!")
        except Exception as e:
            messages.error(request,str(e))

    context = {

    }
    return render(request,'index.html',context)