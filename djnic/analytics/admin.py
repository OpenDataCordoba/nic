from django.contrib import admin
from analytics.models import Analytic


@admin.register(Analytic)
class AnalyticAdmin(admin.ModelAdmin):
    list_display = ['evento', 'referencia', 'user', 'object_created']
    list_filter = ['evento', 'referencia', 'user']
