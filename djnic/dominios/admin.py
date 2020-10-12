from django.contrib import admin
from .models import Dominio

@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'zona', 'registrante', 'registered', 'changed', 'expire']
