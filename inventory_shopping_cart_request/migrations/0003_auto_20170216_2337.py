# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 04:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_shopping_cart_request', '0002_auto_20170216_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesttable',
            name='shopping_cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='inventory_shopping_cart.ShoppingCart'),
        ),
    ]
