# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 08:55
from __future__ import unicode_literals

from django.db import migrations


def transaction_signatures(apps, schema_editor):
    TransactionModel = apps.get_model('walletweb', 'Transaction')

    # just save the transaction, it will generate the sig
    for t in TransactionModel.objects.all():
        t.save()


class Migration(migrations.Migration):

    dependencies = [
        ('walletweb', '0006_transaction_signature'),
    ]

    operations = [
        migrations.RunPython(transaction_signatures)
    ]
