# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_email_support', '0004_prependedbody'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanreminderschedule',
            name='date',
            field=models.DateField(unique=True),
        ),
    ]
