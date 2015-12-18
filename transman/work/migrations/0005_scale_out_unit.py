# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0004_auto_20151218_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='scale',
            name='out_unit',
            field=models.FloatField(default=10, verbose_name=b'\xe5\x87\xba\xe8\xb4\xa7\xe5\x8d\x95\xe4\xbb\xb7'),
            preserve_default=False,
        ),
    ]
