# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-09 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_requests', '0008_auto_20170408_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='backfill',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]