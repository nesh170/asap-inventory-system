# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-03 20:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_auto_20170402_2248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='item',
        ),
        migrations.DeleteModel(
            name='Asset',
        ),
    ]