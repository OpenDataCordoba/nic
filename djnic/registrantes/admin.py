from django.contrib import admin
from .models import Registrante

@admin.register(Registrante)
class RegistranteAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_uid', 'created', 'changed']
    list_per_page = 10
    search_fields = ['name', 'legal_uid']
