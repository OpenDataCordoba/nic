from django.contrib import admin
from .models import Dominio

@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):

    def nameservers(self, obj):
        return ' '.join([f'{dns.orden}: {dns.dns.dominio}' for dns in obj.dnss.order_by('orden')])

    list_display = ['nombre', 'zona', 'estado', 'data_updated', 'data_readed', 'registrante', 'registered', 'changed', 'expire', 'nameservers']
    list_per_page = 10
    list_select_related = ('zona', 'registrante')
    search_fields = ['nombre']
    list_filter = ['estado']
