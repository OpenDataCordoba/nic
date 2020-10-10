from django.db import models


class Zona(models.Model):
    nombre = models.CharField(max_length=30)

