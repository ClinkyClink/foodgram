from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'password',
        'first_name',
        'last_name',
    )
    list_editable = ('password', )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = 'пусто'


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'author'
    )
    search_fields = ('user',)
    empty_value_display = 'пусто'

