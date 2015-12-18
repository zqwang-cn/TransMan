# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0002_auto_20151217_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutRec',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('car_no', models.CharField(max_length=10)),
                ('driver_name', models.CharField(max_length=10)),
                ('contact_info', models.CharField(max_length=20)),
                ('amount', models.FloatField()),
                ('setoff_time', models.DateTimeField(auto_now_add=True)),
                ('qrcode', models.CharField(max_length=10, unique=True, null=True)),
            ],
        ),
    ]
