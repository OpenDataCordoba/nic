from django.contrib import admin
from .models import Dominio

@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'zona', 'data_updated', 'registrante', 'registered', 'changed', 'expire']
    list_per_page = 10
    list_select_related = ('zona', 'registrante')
