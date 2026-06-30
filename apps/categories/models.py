import logging
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

logger = logging.getLogger("blog")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


@receiver(post_save, sender=Category)
def log_category_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Category created: '{instance.name}'")
    else:
        logger.info(f"Category updated: '{instance.name}' (id={instance.id})")


@receiver(pre_delete, sender=Category)
def log_category_delete(sender, instance, **kwargs):
    logger.warning(f"Category deleted: '{instance.name}' (id={instance.id})")
