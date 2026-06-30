import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger("blog")


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles"
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


@receiver(post_save, sender=Article)
def log_article_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Article created: '{instance.title}' by '{instance.author.username}'")
    else:
        logger.info(f"Article updated: '{instance.title}' (id={instance.id})")


@receiver(pre_delete, sender=Article)
def log_article_delete(sender, instance, **kwargs):
    logger.warning(
        f"Article deleted: '{instance.title}' (id={instance.id}) by '{instance.author.username}'"
    )
