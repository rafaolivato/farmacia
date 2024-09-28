# Generated by Django 5.0.6 on 2024-06-20 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0031_remove_medicamento_dosagem_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicamento',
            name='psicotropico',
            field=models.CharField(blank=True, choices=[('A', 'Lista A'), ('B', 'Lista B'), ('C', 'Lista C')], max_length=1, null=True, verbose_name='Psicotrópico'),
        ),
    ]
