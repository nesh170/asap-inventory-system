# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 06:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_auto_20170214_0129'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='floatfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='intfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='longtextfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='shorttextfield',
            unique_together=set([('item', 'field')]),
        ),
    ]
