# Generated by Django 5.0.9 on 2024-12-04 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_contract_iva_str'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='iva_str',
        ),
    ]
