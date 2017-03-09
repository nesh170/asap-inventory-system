# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-09 21:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_auto_20170216_2337'),
        ('inventory_requests', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='disbursement',
            unique_together=set([('cart', 'item')]),
        ),
        migrations.AlterUniqueTogether(
            name='loan',
            unique_together=set([('cart', 'item')]),
        ),
    ]
