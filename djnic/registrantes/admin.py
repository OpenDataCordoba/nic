from django.contrib import admin
from .models import Registrante

@admin.register(Registrante)
class RegistranteAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_uid', 'created', 'changed']
