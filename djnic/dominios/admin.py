from django.contrib import admin
from .models import Dominio, PreDominio


@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):

    def nameservers(self, obj):
        ret = ' '.join([f'{dns.orden}: {dns.dns.dominio}' for dns in obj.dnss.order_by('orden')])
        # limit width in admin
        if len(ret) > 20:
            ret = ret[:17] + '...'
        return ret

    # truncate the registrante width in admin
    def registrante(self, obj):
        if obj.registrante:
            ret = str(obj.registrante)
            if len(ret) > 20:
                ret = ret[:17] + '...'
            return ret
        return '-'

    list_display = [
        'nombre', 'zona', 'estado', 'priority_to_update', 'next_update_priority', 'data_updated', 'data_readed',
        'registrante', 'registered', 'changed', 'expire', 'nameservers'
    ]
    list_select_related = ('zona', 'registrante')
    search_fields = ['nombre']
    list_filter = ['estado', 'zona']
    # remove huge selectors for the change view (like registrante)
    readonly_fields = ['registrante']
    # 25 records per page
    list_per_page = 25

@admin.register(PreDominio)
class PreDominioAdmin(admin.ModelAdmin):

    list_display = ['dominio', 'priority', 'object_created']
    search_fields = ['dominio']
    list_filter = ['priority']
    # 25 records per page
    list_per_page = 25
