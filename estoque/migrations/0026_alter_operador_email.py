# Generated by Django 5.0.6 on 2024-06-18 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0025_operador'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operador',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]