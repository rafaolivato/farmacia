# Generated by Django 5.0.6 on 2024-06-18 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0026_alter_operador_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operador',
            name='estabelecimento',
        ),
        migrations.AddField(
            model_name='operador',
            name='estabelecimentos',
            field=models.ManyToManyField(to='estoque.estabelecimento'),
        ),
    ]