# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-02 02:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_logger', '0006_log_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='color',
            field=models.CharField(max_length=9, unique=True),
        ),
    ]