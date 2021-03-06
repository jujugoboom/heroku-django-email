from django.http import HttpResponse
from django.core import serializers
from django.http import JsonResponse
import hashlib, hmac
import requests
import base64
import os
from .models import *
import boto3

API_KEY = os.environ.get('API_KEY')
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
PUSH_TOKEN = os.environ.get("PUSH_TOKEN")
PUSH_USER = os.environ.get("PUSH_USER")
USERPASS = base64.b64encode(str(USERNAME + ':' + PASSWORD).encode())
aws_access_key_id = os.environ.get('S3_ACCESS_KEY')
aws_secret_access_key = os.environ.get('S3_SECRET_KEY')
S3_BUCKET = os.environ.get('AWS_BUCKET_NAME')

def index(request):
    return HttpResponse("OK")

def handle_request(request):
    if request.method == 'POST':
        return recieve_message(request)
    elif request.method == 'GET':
        return retreive_message(request)
    elif request.method == 'DELETE':
        delete_message(request)
    return HttpResponse('OK')

def recieve_message(request):
    email = Message()
    email.sender = request.POST.get('sender')
    email.recipient = request.POST.get('recipient')
    email.subject = request.POST.get('subject', '')
    email.message = request.POST.get('body-plain', '')
    email.timestamp = int(request.POST.get('timestamp'))
    if verify(API_KEY.encode(), request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
        attachments = ''
        if len(request.FILES.keys()) > 0:
            s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            for key in request.FILES:
                file = request.FILES[key]
                filename = file.name
                temp = filename.split('.')
                filename = ''.join(temp[:-1]) + str(email.timestamp) + '.' + str(temp[-1])
                attachments += filename + ', '
                s3.Bucket(S3_BUCKET).put_object(Key=filename, Body=file)
        email.attachments = attachments
        email.save()
        notification = {'token' : PUSH_TOKEN, 'user' : PUSH_USER, 'title' : 'New Email', 'message' : 'New Email from ' + email.sender + ' "' + email.subject + '"'}
        requests.post("https://api.pushover.net/1/messages.json", data=notification)
        return HttpResponse('OK')

def retreive_message(request):
    if request.META['HTTP_AUTHORIZATION'] == 'Basic ' + USERPASS.decode():
            if list(Message.objects.all()) == []:
                return HttpResponse('No Messages')
            lastmessage = Message.objects.order_by('-id')[0]
            firstmessage = Message.objects.order_by('id')[0]
            if int(lastmessage.id) - int(firstmessage.id) <= 50:
                messages = Message.objects.all().order_by('-id')
            else:
                id = int(lastmessage.id) - int(request.META['HTTP_ID'])
                messages = Message.objects.all().order_by('-id')[id-50:id]
            return JsonResponse(serializers.serialize('json', messages), safe=False)

def delete_message(request):
    if request.META['HTTP_AUTHORIZATION'] == 'Basic ' + USERPASS.decode():
            i = int(request.META['HTTP_ID'])
            email = Message.objects.all().order_by('-id')[i]
            trash = TrashEmail()
            trash.sender = email.sender
            trash.recipient = email.recipient
            trash.subject = email.subject
            trash.message = email.message
            trash.timestamp = email.timestamp
            trash.attachments = email.attachments
            trash.save()
            email.delete()

def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token).encode(),
                             digestmod=hashlib.sha256).hexdigest()
