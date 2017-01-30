# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-27 21:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='items.Item'),
        ),
    ]
