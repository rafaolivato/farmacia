# Generated by Django 5.0.6 on 2024-06-27 12:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0032_alter_medicamento_psicotropico'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferenciaMedicamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_atendimento', models.DateField(auto_now_add=True)),
                ('quantidade', models.PositiveIntegerField()),
                ('estabelecimento_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_destino', to='estoque.estabelecimento')),
                ('estabelecimento_origem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_origem', to='estoque.estabelecimento')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.medicamento')),
            ],
        ),
    ]