# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 02:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_requests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.Item'),
        ),
    ]