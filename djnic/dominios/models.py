from django.db import models


class Dominio(models.Model):
    zona = models.ForeignKey('zonas.Zona', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=240)