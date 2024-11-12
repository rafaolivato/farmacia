from django.apps import AppConfig


class EstoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estoque'


class EstoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estoque'

    def ready(self):
        import estoque.signals  # Certifique-se de alterar para o nome correto do seu app
