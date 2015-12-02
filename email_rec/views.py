from django.http import HttpResponse
from django.shortcuts import render
import hashlib, hmac
import tinys3
import json
from .models import *

S3_ACCESS_KEY = 'AKIAJPA62PHGYTEYJSXA'
S3_SECRET_KEY = 'fnZzvVdXCmKypTjGyJJaaBPVGLcmBLy77pNJP/Yc'
API_KEY = str('key-f5fe8fa67f3fdb15a4a5a7f3788c5acb').encode()
# Create your views here.

def index(request):
    return HttpResponse("OK")

def recieve_email(request):
    if request.method == 'POST':
        email = Message()
        email.sender = request.POST.get('sender')
        email.recipient = request.POST.get('recipient')
        email.subject = request.POST.get('subject', '')
        email.message = request.POST.get('body-plain', '')
        attachments = ''
        if len(request.FILES.keys()) > 0:
            conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,default_bucket='justin-email-attachments')
            for key in request.FILES:
                f = open(request.FILES[key],'rb')
                attachments += f.name + ', '
                conn.upload(f.name,f,'my_bucket')
        email.attachments = attachments
        email.timestamp = int(request.POST.get('timestamp'))
        if verify(API_KEY, request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
            email.save()
    elif request.method == 'GET':
        print(request)
    return HttpResponse('OK')


def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token).encode(),
                             digestmod=hashlib.sha256).hexdigest()