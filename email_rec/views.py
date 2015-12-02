from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
import hashlib, hmac
import tinys3
import requests
import json
import base64
import os
from .models import *

S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
API_KEY = os.environ.get('API_KEY')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
PUSH_TOKEN = os.environ.get("PUSH_TOKEN")
PUSH_USER = os.environ.get("PUSH_USER")
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
                print(request.FILES[key])
                #f = open(request.FILES[key],'rb')
                #attachments += f.name + ', '
                #conn.upload(f.name,f)
        email.attachments = attachments
        email.timestamp = int(request.POST.get('timestamp'))
        if verify(API_KEY.encode(), request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
            email.save()
            notification = {'token' : PUSH_TOKEN, 'user' : PUSH_USER, 'title' : 'New Email', 'message' : 'New Email from ' + email.sender + ' "' + email.subject + '"'}
            requests.post("https://api.pushover.net/1/messages.json", data=notification)
    elif request.method == 'GET':
        if request.META['HTTP_AUTHORIZATION'] == 'Basic ' + USERPASS.decode():
            lastmessage = Message.objects.order_by('-id')[0]
            firstmessage = Message.objects.order_by('id')[0]
            if int(lastmessage.id) - int(firstmessage.id) < 50:
                messages = Message.objects.all().order_by('-id')
            else:
                id = int(lastmessage.id) - int(request.META['HTTP_ID'])
                if id - int(firstmessage.id) < 50:
                    messages = Message.objects.all().order_by('-id')[id:]
                else:
                    messages = Message.objects.all().order_by('-id')[id:id+50]
            return JsonResponse(serializers.serialize('json', messages), safe=False)
    return HttpResponse('OK')


def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token).encode(),
                             digestmod=hashlib.sha256).hexdigest()