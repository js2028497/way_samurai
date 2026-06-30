import secrets
import logging
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger("blog")


class Token(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="auth_token"
    )
    key = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_key(cls) -> str:
        return secrets.token_hex(128)

    def __str__(self) -> str:
        return f"{self.key[:20]}... ({self.user.username})"


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    logger.info(f"User '{user.username}' logged in from {ip}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User '{user.username}' logged out")


@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"User created: '{instance.username}'")
    else:
        logger.info(f"User updated: '{instance.username}'")


@receiver(pre_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    logger.warning(f"User deleted: '{instance.username}' (id={instance.id})")


@receiver(post_save, sender=Token)
def log_token_create(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Token created for user '{instance.user.username}'")
