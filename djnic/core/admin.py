from django.contrib import admin
from core.models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'object_created', 'description']

