# Generated by Django 4.2.8 on 2024-06-03 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0012_detalhesmedicamento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicamento',
            name='codigo_identificacao',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
