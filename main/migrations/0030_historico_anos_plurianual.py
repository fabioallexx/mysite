# Generated by Django 5.0.9 on 2024-12-04 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_remove_contract_iva_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='historico',
            name='anos_plurianual',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
