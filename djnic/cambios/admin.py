from django.contrib import admin
from .models import CambiosDominio, CampoCambio


@admin.register(CambiosDominio)
class CambiosDominioAdmin(admin.ModelAdmin):
    def dominio_cambiado(self, obj):
        return obj.dominio.full_domain()

    list_display = ['dominio_cambiado', 'momento', 'have_changes']
    list_per_page = 10
    list_select_related = ('dominio', )
    list_filter = ['have_changes']
    search_fields = ['dominio__nombre']


@admin.register(CampoCambio)
class CampoCambioAdmin(admin.ModelAdmin):
    def dominio(self, obj):
        return obj.cambio.dominio.full_domain()

    def momento(self, obj):
        return obj.cambio.momento

    list_display = ['dominio', 'momento', 'campo', 'anterior', 'nuevo']
    list_per_page = 10
    list_filter = ['campo']
    search_fields = ['cambio__dominio__nombre', 'campo', 'anterior', 'nuevo']
