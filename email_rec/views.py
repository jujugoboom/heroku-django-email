from django.http import HttpResponse
from django.shortcuts import render
import hashlib, hmac
import tinys3
import json
from .models import *

S3_ACCESS_KEY = 'AKIAJPA62PHGYTEYJSXA'
S3_SECRET_KEY = 'fnZzvVdXCmKypTjGyJJaaBPVGLcmBLy77pNJP/Yc'
API_KEY = 'f5fe8fa67f3fdb15a4a5a7f3788c5acb'
# Create your views here.

def index(request):
    return HttpResponse("OK")

def recieve_email(request):
    body_unicode = request.body.decode('utf-8')
    print(json.dumps(body_unicode))
    print('NEW MESSAGE')
    if request.method == 'POST':
        print("CREATING MESSAGE")
        email = Message()
        print("MESSAGE CREATED")
        email.sender = request.POST.get('sender')
        print("ADDED SENDER")
        email.recipient = request.POST.get('recipient')
        print("ADDED RECIPIENT")
        email.subject = request.POST.get('subject', '')
        print("ADDED SUBJECT")
        email.message = request.POST.get('body-plain', '')
        print("ADDED MESSAGE")
        attachments = ''
        print("ADDING ATTACHMENTS")
        if len(request.FILES.keys()) > 0:
            print("CONNECTING TO S3")
            conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,default_bucket='justin-email-attachments')
            print("CONNECTED TO S3")
            for key in request.FILES:
                print("ADDING FILE TO S3")
                f = open(request.FILES[key],'rb')
                attachments += f.name + ', '
                conn.upload(f.name,f,'my_bucket')
        email.attachments = attachments
        print("ADDED ATTACHMENTS")
        email.timestamp = request.POST.get('timestamp')
        print("ADDED TIME STAMP")
        if verify(API_KEY, request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
            print("VERIFIED")
            email.save()
            print("SAVED")
        else:
            print("NOT VERIFIED")
    return HttpResponse('OK')


def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token),
                             digestmod=hashlib.sha256).hexdigest()