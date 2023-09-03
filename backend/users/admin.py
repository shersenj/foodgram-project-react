from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, AuthorSubscription


admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )
    list_filter = ('username', 'email')
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    ordering = ('username',)


@admin.register(AuthorSubscription)
class AuthorSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
