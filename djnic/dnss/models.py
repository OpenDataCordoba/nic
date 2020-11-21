import logging
import re
from django.db import models

logger = logging.getLogger(__name__)

class Empresa(models.Model):
    """ una empresa de hosting """
    nombre = models.CharField(max_length=90)
    
    def __str__(self):
        return self.nombre

    def detect_DNSs(self):
        """ returns a list of querysets with all DNSs """
        ret = []
        for rg in self.regexs:
            ret.append(DNS.objects.filter(dominio__regex=rg.regex_dns))
        return ret

    def connect_all(self):
        """ conectar esta empresa a todos los DNSs detectados """
        querysets = self.detect_DNSs()
        for qs in querysets:
            qs.update(empresa=self)


class EmpresaRegexDomain(models.Model):
    """ cada una de las expresiones regulares para detectar dominios que le pertenecen """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='regexs')
    regex_dns = models.CharField(max_length=190, help_text='Experesion regular para encontrar los DNSs que le pertenecen', null=True, blank=True)

    def __str__(self):
        returf f'{self.empresa} {self.regex_dns}'


class DNS(models.Model):
    empresa_regex = models.ForeignKey(EmpresaRegexDomain, null=True, blank=True, on_delete=models.SET_NULL, related_name='nameservers')
    dominio = models.CharField(max_length=240, unique=True)

    def __str__(self):
        return self.dominio

    def assign_empresa(self):
        for rgs in EmpresaRegexDomain.objects.all():
            if re.search(rgs.regex_dns ,self.dominio) is not None:
                self.empresa_regex = rgs
                return
        logger.error(f'No regex found for {self.dominio}')
    
    def save(self, **kwargs):
        # buscar la empresa a la que pertenece
        self.assign_empresa()
        return super().save(**kwargs)