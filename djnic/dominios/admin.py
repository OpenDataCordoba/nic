from django.contrib import admin
from .models import Dominio, PreDominio


@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):

    def nameservers(self, obj):
        return ' '.join([f'{dns.orden}: {dns.dns.dominio}' for dns in obj.dnss.order_by('orden')])

    def get_list_per_page(self, request):
        page_size = request.GET.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.list_per_page

    list_display = [
        'nombre', 'zona', 'estado', 'priority_to_update', 'next_update_priority', 'data_updated', 'data_readed',
        'registrante', 'registered', 'changed', 'expire', 'nameservers'
    ]
    list_per_page = 10
    page_size = 50
    list_select_related = ('zona', 'registrante')
    search_fields = ['nombre']
    list_filter = ['estado', 'zona']
    # remove huge selectors for the change view (like registrante)
    readonly_fields = ['registrante']


@admin.register(PreDominio)
class PreDominioAdmin(admin.ModelAdmin):

    def get_list_per_page(self, request):
        page_size = request.GET.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.list_per_page

    list_display = ['dominio', 'priority', 'object_created']
    list_per_page = 10
    page_size = 50
    search_fields = ['dominio']
    list_filter = ['priority']
