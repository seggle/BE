from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from . import models

# admin.site.register(User, UserAdmin)

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'email',
        'name',
        'privilege',
        'date_joined',
    )

    list_display_links = (
        'username',
        'email',
    )