# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-08 19:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_requests', '0007_disbursement_from_backfill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backfill',
            name='status',
            field=models.CharField(choices=[('backfill_request', 'backfill_request'), ('backfill_transit', 'backfill_transit'), ('backfill_satisfied', 'backfill_satisfied'), ('backfill_failed', 'backfill_failed'), ('backfill_denied', 'backfill_denied')], max_length=40),
        ),
    ]
