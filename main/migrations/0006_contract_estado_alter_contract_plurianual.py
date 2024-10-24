# Generated by Django 5.1.1 on 2024-10-23 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_contract_plurianual'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='estado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='plurianual',
            field=models.TextField(blank=True, null=True),
        ),
    ]