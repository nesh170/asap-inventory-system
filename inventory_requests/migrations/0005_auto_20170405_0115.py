# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-05 05:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_requests', '0004_auto_20170402_2253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backfill',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='backfill',
            name='item',
        ),
        migrations.AddField(
            model_name='backfill',
            name='loan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='backfill_loan', to='inventory_requests.Loan'),
        ),
        migrations.AddField(
            model_name='backfill',
            name='status',
            field=models.CharField(choices=[('backfill_request_loan', 'backfill_request_loan'), ('backfill_request_outright', 'backfill_request_outright'), ('backfill_transit', 'backfill_transit'), ('backfill_satisfied', 'backfill_satisfied'), ('backfill_failed', 'backfill_failed')], max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='requestcart',
            name='status',
            field=models.CharField(choices=[('outstanding', 'outstanding'), ('approved', 'approved'), ('cancelled', 'cancelled'), ('denied', 'denied'), ('active', 'active'), ('fulfilled', 'fulfilled')], default='active', max_length=40),
        ),
    ]