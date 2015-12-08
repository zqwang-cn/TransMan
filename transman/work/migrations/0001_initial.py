# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-08 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TransRec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_no', models.CharField(max_length=10)),
                ('driver_name', models.CharField(max_length=10)),
                ('contact_info', models.CharField(max_length=20)),
                ('setoff_amount', models.FloatField(null=True)),
                ('arrive_amount', models.FloatField(null=True)),
                ('setoff_time', models.DateTimeField(auto_now=True)),
                ('arrive_time', models.DateTimeField(null=True)),
            ],
        ),
    ]
