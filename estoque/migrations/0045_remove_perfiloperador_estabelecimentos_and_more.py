# Generated by Django 4.2.16 on 2024-10-17 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0044_alter_operador_password_alter_operador_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfiloperador',
            name='estabelecimentos',
        ),
        migrations.RemoveField(
            model_name='perfiloperador',
            name='funcionalidades',
        ),
        migrations.RemoveField(
            model_name='perfiloperador',
            name='user',
        ),
        migrations.RemoveField(
            model_name='operador',
            name='perfil',
        ),
        migrations.DeleteModel(
            name='Funcionalidade',
        ),
        migrations.DeleteModel(
            name='PerfilOperador',
        ),
    ]