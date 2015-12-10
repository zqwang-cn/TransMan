# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0002_transrec_payed'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transrec',
            options={'permissions': (('mine', 'mine permission'), ('scale', 'scale permission'), ('account', 'account permission'))},
        ),
    ]
