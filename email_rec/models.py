from django.db import models

# Create your models here.

class Message(models.Model):
    sender = models.TextField
    recipient = models.TextField
    subject = models.TextField
    message = models.TextField
    timestamp = models.IntegerField
    attachments = models.TextField


