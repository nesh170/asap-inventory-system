# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-02 00:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_logger', '0002_auto_20170201_1905'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='log_timestamp',
            new_name='timestamp',
        ),
    ]
