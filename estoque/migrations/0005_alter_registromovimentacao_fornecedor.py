# Generated by Django 4.2.8 on 2024-05-29 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0004_fornecedor_registromovimentacao_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registromovimentacao',
            name='fornecedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.fornecedor'),
        ),
    ]
