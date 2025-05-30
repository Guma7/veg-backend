from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    description = models.TextField(blank=True, default='')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

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
        import logging
        logger = logging.getLogger('django')
        logger.error(f"Erro ao salvar perfil do usuário: {str(e)}")