from django.http import HttpResponse
from django.shortcuts import render
import hashlib, hmac
import tinys3
import json
import base64
import os
from .models import *

S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
API_KEY = os.environ.get('API_KEY')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
USERPASS = base64.b64encode(str(USERNAME + ':' + PASSWORD).encode())

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
        if verify(API_KEY.encode(), request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
            email.save()
    elif request.method == 'GET':
        if request.META['HTTP_AUTHORIZATION'] == 'Basic ' + USERPASS.decode():
            print(request.META['id'])
    return HttpResponse('OK')


def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token).encode(),
                             digestmod=hashlib.sha256).hexdigest()