# Generated by Django 5.1.1 on 2024-10-25 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_fatura'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fatura',
            old_name='data_final',
            new_name='data',
        ),
        migrations.RenameField(
            model_name='fatura',
            old_name='tipo_contrato',
            new_name='mydoc',
        ),
        migrations.RenameField(
            model_name='fatura',
            old_name='preco_contratual',
            new_name='valor',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='_estado',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='compromisso',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='data_inicial',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='fornecedor',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='observacao',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='plurianual',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='prazo',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='procedimento',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='recorrente',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='uploaded_file',
        ),
        migrations.RemoveField(
            model_name='fatura',
            name='valor_entregue',
        ),
    ]
