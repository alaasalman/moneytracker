# Generated by Django 2.0.3 on 2018-04-07 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walletweb', '0028_auto_20180407_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]
