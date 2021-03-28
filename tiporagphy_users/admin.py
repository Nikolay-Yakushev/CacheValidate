# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from tiporagphy_users import redis_pi


class CustomUserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        """user_change_id = id of a user in
        django admin for which save method has bee called"""
        user_changed_id = form.instance.id
        redis_pi.delete(user_changed_id)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        redis_pi.delete(obj.id)
        obj.delete()


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
