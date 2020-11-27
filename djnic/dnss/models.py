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
        """ connect all DNSs to regexs """
        for rg in self.regexs.all():
            rg.detect_DNSs()
        


class EmpresaRegexDomain(models.Model):
    """ cada una de las expresiones regulares para detectar dominios que le pertenecen """
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='regexs')
    regex_dns = models.CharField(max_length=190,
                                 help_text='Experesion regular para encontrar los DNSs que le pertenecen', 
                                 null=True, blank=True, unique=True)
    
    def detect_DNSs(self):
        logger.info(f'Look for domains to Empresa {self.empresa.nombre} {self.regex_dns}')
        # remove previous
        qs = DNS.objects.filter(empresa_regex=self)
        logger.info(f'Previous {qs.count()} domains to Empresa found')
        updated = qs.update(empresa_regex=None)
        logger.info(f'previous {updated} domains to Empresa updated')
        
        qs = DNS.objects.filter(dominio__regex=self.regex_dns)
        logger.info(f'{qs.count()} domains to Empresa found')
        updated = qs.update(empresa_regex=self)
        logger.info(f'{updated} domains to Empresa updated')
        
    def __str__(self):
        return f'{self.empresa} {self.regex_dns}'


class DNS(models.Model):
    empresa_regex = models.ForeignKey(EmpresaRegexDomain, null=True, blank=True, on_delete=models.SET_NULL, related_name='nameservers')
    dominio = models.CharField(max_length=240, unique=True)

    def __str__(self):
        return self.dominio

    def assign_empresa(self):
        for rgs in EmpresaRegexDomain.objects.all():
            logger.info(f'Check {rgs.regex_dns} to assign {self.dominio}')
            if re.search(rgs.regex_dns, self.dominio) is not None:
                logger.info(f'DNS {self.dominio} empresa_regex={rgs.regex_dns}')
                self.empresa_regex = rgs
                return
        logger.error(f'No regex found for {self.dominio}')
    
    def save(self, **kwargs):
        if self.empresa_regex is None:
            logger.info('Adding empresa_regex')
            # buscar la empresa a la que pertenece
            self.assign_empresa()
        return super().save(**kwargs)