# Generated by Django 5.1 on 2024-11-15 20:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalhesmedicamento',
            name='estabelecimento',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estoque.estabelecimento'),
            preserve_default=False,
        ),
    ]
