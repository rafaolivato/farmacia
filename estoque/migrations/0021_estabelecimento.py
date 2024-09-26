# Generated by Django 4.2.8 on 2024-06-11 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0020_fabricante'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estabelecimento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('codigo_cnes', models.CharField(max_length=20)),
                ('farmaceutico_responsavel', models.CharField(max_length=255)),
                ('imagem_logotipo', models.ImageField(upload_to='logotipos/')),
                ('tipo_estabelecimento', models.CharField(choices=[('Farmacia', 'Farmácia'), ('Almoxarifado Central', 'Almoxarifado Central')], max_length=20)),
            ],
        ),
    ]
