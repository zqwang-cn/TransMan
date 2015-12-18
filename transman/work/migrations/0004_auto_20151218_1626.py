# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0003_outrec'),
    ]

    operations = [
        migrations.AddField(
            model_name='outrec',
            name='unit',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='outrec',
            name='qrcode',
            field=models.CharField(default='aaa', unique=True, max_length=10, blank=True),
            preserve_default=False,
        ),
    ]
