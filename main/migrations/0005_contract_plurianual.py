# Generated by Django 5.1.1 on 2024-10-22 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_cadernoencargos_contrato_celebrado'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='plurianual',
            field=models.CharField(default=2024, max_length=1000),
            preserve_default=False,
        ),
    ]
