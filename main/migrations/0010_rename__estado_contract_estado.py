# Generated by Django 5.1.1 on 2024-10-23 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_historico'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='_estado',
            new_name='estado',
        ),
    ]