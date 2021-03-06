# Generated by Django 2.0.2 on 2018-02-02 11:56

from django.db import migrations


def assignusertotransactions(apps, schema_editor):
  """
  Assign user to transaction fetched from its associated account
  """
  AccountModel = apps.get_model('walletweb', 'Account')

  for acct in AccountModel.objects.all():
    for t in acct.transactions.all():
      t.user = acct.user
      t.save()


class Migration(migrations.Migration):

    dependencies = [
        ('walletweb', '0019_transaction_user'),
    ]

    operations = [
      migrations.RunPython(assignusertotransactions)
    ]
