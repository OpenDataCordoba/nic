from django.contrib import admin
from .models import DNS

@admin.register(DNS)
class DNSAdmin(admin.ModelAdmin):
    list_display = ['dominio']
    list_per_page = 10
    search_fields = ['dominio']
