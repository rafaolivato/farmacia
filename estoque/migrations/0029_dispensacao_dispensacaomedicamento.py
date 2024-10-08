# Generated by Django 5.0.6 on 2024-06-18 21:05

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0028_medico_alter_medicamento_psicotropico'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dispensacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outros_prescritores', models.CharField(blank=True, max_length=255, null=True)),
                ('numero_notificacao', models.CharField(blank=True, max_length=6, null=True)),
                ('data_receita', models.DateField(default=django.utils.timezone.now)),
                ('data_dispensacao', models.DateField(auto_now_add=True)),
                ('medico', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='estoque.medico')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.paciente')),
            ],
        ),
        migrations.CreateModel(
            name='DispensacaoMedicamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField()),
                ('dispensacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicamentos', to='estoque.dispensacao')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.medicamento')),
            ],
        ),
    ]
