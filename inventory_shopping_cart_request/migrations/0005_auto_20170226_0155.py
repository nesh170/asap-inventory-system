# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 06:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_shopping_cart_request', '0004_auto_20170223_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requesttable',
            old_name='quantity_requested',
            new_name='quantity',
        ),
    ]
