from django.contrib import admin
from .models import Registrante, TagForRegistrante, RegistranteTag

@admin.register(Registrante)
class RegistranteAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_uid', 'created', 'changed']
    list_per_page = 10
    search_fields = ['name', 'legal_uid']


@admin.register(TagForRegistrante)
class TagForRegistranteAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    list_per_page = 10
    search_fields = ['nombre']


@admin.register(RegistranteTag)
class RegistranteTagAdmin(admin.ModelAdmin):
    list_display = ['registrante', 'tag']
    list_per_page = 10
    search_fields = ['registrante__name', 'registrante__legal_uid', 'tag__nombre']
    autocomplete_fields = ['registrante', 'tag']
    list_select_related = ['registrante', 'tag']
    list_filter = ['tag']