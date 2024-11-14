from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Só cria um novo perfil quando o usuário é criado
        # Verifica se o perfil já existe, se não, cria um novo
        Profile.objects.get_or_create(user=instance)
