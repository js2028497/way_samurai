from django.contrib import admin
from apps.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "article", "created_at", "updated_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "author__username", "article__title"]
    date_hierarchy = "created_at"
