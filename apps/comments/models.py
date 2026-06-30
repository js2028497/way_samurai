import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger("blog")


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    article = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on '{self.article.title}'"


@receiver(post_save, sender=Comment)
def log_comment_save(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Comment created by '{instance.author.username}' on article '{instance.article.title}'"
        )
    else:
        logger.info(f"Comment updated (id={instance.id})")


@receiver(pre_delete, sender=Comment)
def log_comment_delete(sender, instance, **kwargs):
    logger.warning(
        f"Comment deleted (id={instance.id}) by '{instance.author.username}'"
    )
