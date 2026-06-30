from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from apps.users.models import Token


class TokenInline(admin.StackedInline):
    model = Token
    can_delete = False
    verbose_name_plural = "Token"


class UserAdmin(BaseUserAdmin):
    inlines = [TokenInline]
    list_display = ["username", "email", "is_staff", "date_joined"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["user", "key_short", "created_at"]
    search_fields = ["user__username"]

    def key_short(self, obj):
        return obj.key[:30] + "..."

    key_short.short_description = "Token Key"
