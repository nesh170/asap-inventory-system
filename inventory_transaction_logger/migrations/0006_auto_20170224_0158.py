# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 06:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_transaction_logger', '0005_shoppingcartlog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingcartlog',
            old_name='cart',
            new_name='shopping_cart',
        ),
        migrations.AddField(
            model_name='log',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shoppingcartlog',
            name='log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart_log', to='inventory_transaction_logger.Log'),
        ),
    ]
