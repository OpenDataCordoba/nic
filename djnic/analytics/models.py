from django.contrib.auth.models import User
from django.db import models


class Analytic(models.Model):
    """ mediciones internas varias """

    referencia = models.CharField(max_length=160, db_index=True, help_text='Referencia única. Ej: dominios.csv')
    evento = models.CharField(max_length=90, db_index=True, help_text='Tipo de evento. Ej: descarga')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    extras = models.JSONField(null=True, blank=True)  # extras
    object_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.evento}: {self.referencia}'

    class Meta:
        ordering = ['-object_created']

    @staticmethod
    def request_as_dict(request):
        return {
            'ip': request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR', None)),
            'remote_host': request.META.get('REMOTE_HOST', None),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'accept_language': request.headers.get('Accept-Language', None),
            'referer': request.META.get('HTTP_REFERER', None)
        }
