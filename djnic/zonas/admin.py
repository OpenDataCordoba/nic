from django.contrib import admin
from .models import Zona

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    list_per_page = 10
