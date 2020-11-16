from django.db import models


class GrupoZona(models.Model):
    """ grupo de zonas, paises en general, una zona puede pertenecer a mas de un grupo """
    nombre = models.CharField(max_length=30, unique=True)
    
    def __str__(self):
        return self.nombre


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


class ZonaEnGrupo(models.Model):
    grupo = models.ForeignKey(GrupoZona, on_delete=models.CASCADE, related_name='zonas')
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='grupos')

    def __str__(self):
        return f'{self.zona.nombre} en {self.grupo.nombre}'