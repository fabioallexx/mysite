# Generated by Django 5.1.1 on 2024-10-25 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_contract_objeto'),
    ]

    operations = [
        migrations.AddField(
            model_name='historico',
            name='objeto',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
