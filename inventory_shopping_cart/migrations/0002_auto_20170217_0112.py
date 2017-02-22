# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 06:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_shopping_cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcart',
            name='status',
            field=models.CharField(choices=[('outstanding', 'outstanding'), ('approved', 'approved'), ('cancelled', 'cancelled'), ('denied', 'denied'), ('active', 'active')], default='outstanding', max_length=16),
        ),
    ]
