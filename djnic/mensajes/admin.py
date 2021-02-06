from django.contrib import admin
from mensajes.models import Mensaje, MensajeDestinado

@admin.register(MensajeDestinado)
class MensajeDestinadoAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'destinatario', 'estado']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'created']