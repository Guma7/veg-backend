from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        # Verificar se já existe um perfil para este usuário antes de criar um novo
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil do usuário quando o usuário é salvo"""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Exception as e:
        # Verificar se já existe um perfil antes de criar um novo
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)
        import logging
        logger = logging.getLogger('django')
        logger.error(f"Erro ao salvar perfil do usuário: {str(e)}")