# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 01:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0009_auto_20170409_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_tag',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
