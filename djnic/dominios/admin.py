from django.contrib import admin
from .models import Dominio, PreDominio


@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):

    def nameservers(self, obj):
        return ' '.join([f'{dns.orden}: {dns.dns.dominio}' for dns in obj.dnss.order_by('orden')])

    def changelist_view(self, request, extra_context=None):
        page_size = request.GET.get('page_size')
        if page_size and page_size.isdigit():
            self.list_per_page = int(page_size)
        else:
            self.list_per_page = 20
        return super().changelist_view(request, extra_context)

    list_display = [
        'nombre', 'zona', 'estado', 'priority_to_update', 'next_update_priority', 'data_updated', 'data_readed',
        'registrante', 'registered', 'changed', 'expire', 'nameservers'
    ]
    list_select_related = ('zona', 'registrante')
    search_fields = ['nombre']
    list_filter = ['estado', 'zona']
    # remove huge selectors for the change view (like registrante)
    readonly_fields = ['registrante']


@admin.register(PreDominio)
class PreDominioAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        page_size = request.GET.get('page_size')
        if page_size and page_size.isdigit():
            self.list_per_page = int(page_size)
        else:
            self.list_per_page = 20
        return super().changelist_view(request, extra_context)

    list_display = ['dominio', 'priority', 'object_created']
    search_fields = ['dominio']
    list_filter = ['priority']
