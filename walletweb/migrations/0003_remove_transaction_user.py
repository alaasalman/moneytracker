# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 21:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('walletweb', '0002_remove_account_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='user',
        ),
    ]
