from django.db import models


class Registrante(models.Model):
    
    name = models.CharField(max_length=240)
    legal_uid = models.CharField(max_length=90, unique=True)
    created = models.DateTimeField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} {self.legal_uid}'