# Generated by Django 5.0.6 on 2024-06-18 22:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0029_dispensacao_dispensacaomedicamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetalheDispensacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField()),
                ('dispensacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalhes', to='estoque.dispensacao')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estoque.medicamento')),
            ],
        ),
    ]