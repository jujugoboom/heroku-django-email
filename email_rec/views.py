from django.http import HttpResponse
from django.shortcuts import render
import hashlib, hmac
import tinys3
from .models import *
import logging
import json

S3_ACCESS_KEY = 'AKIAJPA62PHGYTEYJSXA'
S3_SECRET_KEY = 'fnZzvVdXCmKypTjGyJJaaBPVGLcmBLy77pNJP/Yc'
API_KEY = 'f5fe8fa67f3fdb15a4a5a7f3788c5acb'
# Create your views here.
logger = logging.getLogger(__name__)

def index(request):
    if request.method == 'POST':
        recieve_email(request)

def recieve_email(request):
    logger.warn(json.dumps(request))
    email = Message
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
    email.timestamp = request.POST.get('timestamp')
    if verify(API_KEY, request.POST.get('token'), request.POST.get('timestamp'), request.POST.get('signature')):
        email.save()
    return HttpResponse('OK')


def verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token),
                             digestmod=hashlib.sha256).hexdigest()