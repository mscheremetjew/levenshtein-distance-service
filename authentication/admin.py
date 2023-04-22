from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from authentication.models import User


class UserAdmin(BaseUserAdmin):
    """Custom user admin panel"""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_superuser", "is_staff", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("password1", "password2")}),)
    list_display = ("username", "email", "is_superuser")
    list_filter = ("email", "is_superuser", "is_active")
    search_fields = ("email", "email")
    ordering = ("email",)
    filter_horizontal = ("user_permissions",)


admin.site.register(User, UserAdmin)
