from django.db import models

# Create your models here.

class Message(models.Model):
    sender = models.TextField(null=True, blank=True)
    recipient = models.TextField(null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    timestamp = models.IntegerField(default=0)
    attachments = models.TextField(null=True, blank=True)

class FileModel(models.Model):
    file = models.FileField(upload_to='.')

