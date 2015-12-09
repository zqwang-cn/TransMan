# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CoalType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('unit', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Mine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('balance', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='TransRec',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('car_no', models.CharField(max_length=10)),
                ('driver_name', models.CharField(max_length=10)),
                ('contact_info', models.CharField(max_length=20)),
                ('setoff_amount', models.FloatField(null=True)),
                ('arrive_amount', models.FloatField(null=True)),
                ('setoff_time', models.DateTimeField(auto_now=True)),
                ('arrive_time', models.DateTimeField(null=True)),
                ('qrcode', models.CharField(max_length=10, unique=True, null=True)),
                ('coal_type', models.ForeignKey(to='work.CoalType')),
                ('mine', models.ForeignKey(to='work.Mine')),
            ],
        ),
        migrations.CreateModel(
            name='UserMine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mine', models.ForeignKey(to='work.Mine')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
