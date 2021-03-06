# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-21 03:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(choices=[('short_text', 'short-form text'), ('long_text', 'long-form text'), ('int', 'integer'), ('float', 'floating-point number')], max_length=16)),
                ('private', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FloatField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(blank=True, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floats', to='items.Field')),
            ],
        ),
        migrations.CreateModel(
            name='IntField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(blank=True, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ints', to='items.Field')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('model_number', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LongTextField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='long_texts', to='items.Field')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='long_text_fields', to='items.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ShortTextField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=72, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_texts', to='items.Field')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_text_fields', to='items.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='items.Item')),
            ],
        ),
        migrations.AddField(
            model_name='intfield',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='int_fields', to='items.Item'),
        ),
        migrations.AddField(
            model_name='floatfield',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='float_fields', to='items.Item'),
        ),
        migrations.AlterUniqueTogether(
            name='shorttextfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='longtextfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='intfield',
            unique_together=set([('item', 'field')]),
        ),
        migrations.AlterUniqueTogether(
            name='floatfield',
            unique_together=set([('item', 'field')]),
        ),
    ]
