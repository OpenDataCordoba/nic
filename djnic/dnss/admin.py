from django.contrib import admin
from .models import DNS, Empresa, EmpresaRegexDomain


@admin.register(DNS)
class DNSAdmin(admin.ModelAdmin):
    list_display = ['dominio', 'empresa_regex']
    list_per_page = 10
    search_fields = ['dominio']


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    list_per_page = 10
    search_fields = ['nombre']


@admin.register(EmpresaRegexDomain)
class EmpresaRegexDomainAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'regex_dns']
    list_per_page = 10
    search_fields = ['empresa__nombre', 'regex_dns']
