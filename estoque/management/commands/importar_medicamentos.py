import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from estoque.models import Medicamento

class Command(BaseCommand):
    help = 'Importa medicamentos dos arquivos Excel para o banco de dados'

    def handle(self, *args, **kwargs):
        # Diretório onde os arquivos Excel estão localizados
        excel_dir = os.path.join(settings.MEDIA_ROOT, 'excel')
        excel_files = [
              'codigos_corretos.xlsx'
        ]

        for file_name in excel_files:
            file_path = os.path.join(excel_dir, file_name)
            print(f'Procurando o arquivo: {file_path}')
            if os.path.exists(file_path):
                self.stdout.write(f'Importando dados do arquivo: {file_name}')
                try:
                    df = pd.read_excel(file_path)
                    print(f'Colunas no arquivo {file_name}: {df.columns.tolist()}')
                    for index, row in df.iterrows():
                        Medicamento.objects.update_or_create(
                            codigo_identificacao=row['Código'],
                            defaults={'nome': row['Nome']}
                        )
                    self.stdout.write(self.style.SUCCESS(f'Sucesso ao importar dados do arquivo: {file_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao importar dados do arquivo {file_name}: {e}'))
            else:
                self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {file_name}'))
