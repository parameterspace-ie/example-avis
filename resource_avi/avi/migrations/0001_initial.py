# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DemoModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=50, null=True, editable=False)),
                ('expected_runtime', models.IntegerField(default=0)),
                ('resources_ram_mb', models.IntegerField(default=2000, help_text=b'Amount of RAM (M) to be allocated for the AviJob')),
                ('resources_cpu_cores', models.IntegerField(default=1, help_text=b'Number of CPU cores to be allocated to the AviJob')),
                ('query', models.CharField(max_length=1000)),
                ('outputFile', models.CharField(default=b'', max_length=100)),
                ('request', models.OneToOneField(related_name='demomodel_model', to='pipeline.AviJobRequest')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
