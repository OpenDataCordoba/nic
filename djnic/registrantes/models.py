import pytz
from django.db import models
from django.utils import timezone


class Registrante(models.Model):
    
    name = models.CharField(max_length=240)
    legal_uid = models.CharField(max_length=90, unique=True)
    created = models.DateTimeField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)

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
        return f'{self.name} {self.legal_uid}'