# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-21 14:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0028_auto_20170515_2035'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_version_hash', models.CharField(default='1.0', max_length=200, verbose_name='source_version_hash')),
                ('last_update_time', models.DateTimeField(null=True, verbose_name='last_update_time')),
            ],
            options={
                'ordering': ['last_update_time'],
            },
        ),
        migrations.AddField(
            model_name='module',
            name='source',
            field=models.CharField(default='internal', max_length=200, verbose_name='source'),
        ),
        migrations.AlterField(
            model_name='wfmodule',
            name='module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wf_modules', to='server.ModuleVersion'),
        ),
        migrations.AddField(
            model_name='moduleversion',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_versions', to='server.Module'),
        ),
    ]