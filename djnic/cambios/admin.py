from django.contrib import admin
from .models import CambiosDominio, CampoCambio


@admin.register(CambiosDominio)
class CambiosDominioAdmin(admin.ModelAdmin):
    list_display = ['dominio', 'momento']
    list_per_page = 10
    list_select_related = ('dominio', )


@admin.register(CampoCambio)
class CampoCambioAdmin(admin.ModelAdmin):
    def dominio(self, obj):
        return obj.cambio.dominio

    def momento(self, obj):
        return obj.cambio.momento

    list_display = ['dominio', 'momento', 'campo', 'anterior', 'nuevo']
    list_per_page = 10
