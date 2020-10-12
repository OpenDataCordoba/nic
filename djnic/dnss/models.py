from django.db import models


class Empresa(models.Model):
    """ una empresa de hosting """
    nombre = models.CharField(max_length=90)
    regex_dns = models.CharField(max_length=190, help_text='Experesion regular para encontrar los DNSs que le pertenecen', null=True, blank=True)


class DNS(models.Model):
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL, related_name='nameservers')
    dominio = models.CharField(max_length=240)

    def assign_empresa(self):
        # TODO buscar empresa con regex
        pass
    
    def save(self, **kwargs):
        # buscar la empresa a la que pertenece
        self.assign_empresa()
        return super().save(**kwargs)