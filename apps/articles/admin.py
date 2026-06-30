from django.contrib import admin
from apps.articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "created_at", "updated_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "content", "author__username"]
    date_hierarchy = "created_at"
