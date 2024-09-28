from django.db import models

class Estabelecimento(models.Model):
    TIPOS_ESTABELECIMENTO = [
        ('Farmacia', 'Farmácia'),
        ('Almoxarifado Central', 'Almoxarifado Central'),
    ]

    nome = models.CharField(max_length=255)
    codigo_cnes = models.CharField(max_length=20)
    farmaceutico_responsavel = models.CharField(max_length=255)
    imagem_logotipo = models.ImageField(upload_to='logotipos/')
    tipo_estabelecimento = models.CharField(max_length=20, choices=TIPOS_ESTABELECIMENTO)

    def __str__(self):
        return self.nome