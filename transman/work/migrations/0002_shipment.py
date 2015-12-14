# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unit', models.FloatField()),
                ('coal_type', models.ForeignKey(to='work.CoalType')),
                ('mine', models.ForeignKey(to='work.Mine')),
                ('scale', models.ForeignKey(to='work.Scale')),
            ],
        ),
    ]
