from django.db import models


class Zona(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    tz = models.CharField(max_length=90, null=True, blank=True)

    def save(self, **kwargs):
        # acomodar la zona hoaria en las que cada WhoIs publica
        
        if self.tz is None:
            if self.nombre == 'ar' or self.nombre.endswith('.ar'):
                self.tz = 'America/Argentina/Cordoba'

        return super().save(**kwargs)

    def __str__(self):
        return self.nombre

