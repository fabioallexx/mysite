# Generated by Django 5.1.1 on 2024-10-25 09:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_rename_data_final_fatura_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatura',
            name='contract',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.contract'),
            preserve_default=False,
        ),
    ]
