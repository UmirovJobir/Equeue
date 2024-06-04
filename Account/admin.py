from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'is_staff', 'phone']
    list_display_links = ['id', 'first_name', 'last_name']