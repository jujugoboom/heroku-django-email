from django.forms import ModelForm
from email_rec.models import File

class FileForm(ModelForm):
    class Meta:
        model = File