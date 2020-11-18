from django.contrib import admin
from .models import Zona, GrupoZona, ZonaEnGrupo


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    list_per_page = 10


@admin.register(GrupoZona)
class GrupoZonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'published']
    list_per_page = 10


@admin.register(ZonaEnGrupo)
class ZonaEnGrupoAdmin(admin.ModelAdmin):
    list_display = ['grupo', 'zona', 'published']
    list_per_page = 10
