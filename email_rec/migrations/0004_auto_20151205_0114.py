# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_rec', '0003_filemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrashEmail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('sender', models.TextField(null=True, blank=True)),
                ('recipient', models.TextField(null=True, blank=True)),
                ('subject', models.TextField(null=True, blank=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('timestamp', models.IntegerField(default=0)),
                ('attachments', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.DeleteModel(
            name='FileModel',
        ),
    ]
