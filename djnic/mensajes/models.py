from django.contrib.auth.models import User
from django.db import models
from enum import Enum


class EstadoMensaje(Enum):
    CREATED = 'Creado'
    READED = 'Leido'
    DELETED = 'Borrado'


class Mensaje(models.Model):
    titulo = models.CharField(max_length=120)
    texto = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)


class MensajeDestinado(models.Model):
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=10,
        choices=[(est, est.value) for est in EstadoMensaje],
        default=EstadoMensaje.CREATED.value,
        db_index=True)
    created = models.DateTimeField(auto_now_add=True)
