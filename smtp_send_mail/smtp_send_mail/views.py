from django.shortcuts import render
from django.contrib import messages
def index_page(request):
    if request.method == "POST" :
        messages.info(request,"File uploaded successfully !!!")

    context = {

    }
    return render(request,'index.html',context)