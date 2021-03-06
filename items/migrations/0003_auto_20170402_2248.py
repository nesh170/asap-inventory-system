# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-03 02:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_auto_20170401_0129'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_tag', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='is_asset',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='asset',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='items.Item'),
        ),
    ]
