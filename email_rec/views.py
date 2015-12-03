from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
import hashlib, hmac
import requests
import json
import base64
import time
import os
from .models import *
from .forms import *
from hashlib import sha1
import urllib.parse

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

        email.timestamp = int(request.POST.get('timestamp'))
        if verify(API_KEY.encode(), request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
            attachments = ''
            files = []
            if len(request.FILES.keys()) > 0:
                for key in request.FILES:
                    file = request.FILES[key]
                    print("UPLOADING " + file.name)
                    attachments += file.name
                    signed_request = sign_s3(file.name, file.content_type)
                    response = requests.put(signed_request, data=file)
                    print('SERVER RESPONSE: ' + response.content)
            email.attachments = attachments
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

def sign_s3(filename, filetype):
    AWS_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET = os.environ.get('AWS_BUCKET_NAME')

    object_name = urllib.parse.quote_plus(filename)
    mime_type = filetype

    expires = int(time.time()+60*60*24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

    signature = base64.encodebytes(hmac.new(AWS_SECRET_KEY.encode(), string_to_sign.encode('utf8'), sha1).digest())
    signature = urllib.parse.quote_plus(signature.strip())

    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)
    signed_request = '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature)
    return signed_request