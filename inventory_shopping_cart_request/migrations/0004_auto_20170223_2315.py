# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 04:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_shopping_cart_request', '0003_auto_20170216_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesttable',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='items.Item'),
        ),
    ]