from django.contrib.auth.models import User
from django.db import models


class Mensaje(models.Model):
    titulo = models.CharField(max_length=120)
    texto = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-created']


class MensajeDestinado(models.Model):
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE)

    CREATED = 10
    READED = 20
    DELETED = 30

    estados = (
        (CREATED, 'Creado'),
        (READED, 'Leido'),
        (DELETED, 'Eliminado')
    )

    estado = models.IntegerField(
        choices=estados,
        default=CREATED,
        db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)

    @property
    def unread(self):
        return self.estado == self.CREATED

    def __str__(self):
        return f'{self.mensaje} {self.destinatario}'

    class Meta:
        ordering = ['-created']
