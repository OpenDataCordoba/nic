import pytz
from django.db import models
from django.utils import timezone


class Registrante(models.Model):
    
    name = models.CharField(max_length=240)
    legal_uid = models.CharField(max_length=90, db_index=True)
    zone = models.CharField(max_length=10, default='AR', help_text='Para identificar en el pais donde esta')
    created = models.DateTimeField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    object_created = models.DateTimeField(auto_now_add=True)
    object_modified = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = (('legal_uid', 'zone'))

    
    def get_zoned_date(self, field, zona):
        """ put a datetime in the rigth timezone before move to string """
        
        if field == 'created':
            timefield = self.created
        elif field == 'changed':
            timefield = self.changed
        else:
            raise Exception('Bad field date')

        return timezone.localtime(timefield, pytz.timezone(zona))

    def __str__(self):
        return f'{self.name} [{self.zone}-{self.legal_uid}]'


class TagForRegistrante(models.Model):
    """ etiqueta para los registrantes """
    nombre = models.CharField(max_length=190)
    object_created = models.DateTimeField(auto_now_add=True)
    object_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


class RegistranteTag(models.Model):
    registrante = models.ForeignKey(Registrante, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(TagForRegistrante, on_delete=models.CASCADE, related_name='registrantes')
    object_created = models.DateTimeField(auto_now_add=True)
    object_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tag}->{self.registrante}'

