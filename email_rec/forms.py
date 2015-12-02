from django.forms import ModelForm
from email_rec.models import FileModel

class FileForm(ModelForm):
    class Meta:
        model = FileModel
        fields = '__all__'