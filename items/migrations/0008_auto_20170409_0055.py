# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-09 04:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_item_is_asset'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(choices=[('short_text', 'short-form text'), ('long_text', 'long-form text'), ('int', 'integer'), ('float', 'floating-point number')], max_length=16)),
                ('private', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FloatAssetField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='float_fields', to='items.Asset')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floats', to='items.AssetField')),
            ],
        ),
        migrations.CreateModel(
            name='IntAssetField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='int_fields', to='items.Asset')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ints', to='items.AssetField')),
            ],
        ),
        migrations.CreateModel(
            name='LongTextAssetField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='long_text_fields', to='items.Asset')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='long_texts', to='items.AssetField')),
            ],
        ),
        migrations.CreateModel(
            name='ShortTextAssetField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=72, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_text_fields', to='items.Asset')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_texts', to='items.AssetField')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='shorttextassetfield',
            unique_together=set([('asset', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='longtextassetfield',
            unique_together=set([('asset', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='intassetfield',
            unique_together=set([('asset', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='floatassetfield',
            unique_together=set([('asset', 'field')]),
        ),
    ]
