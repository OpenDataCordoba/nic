from django.db import models
from whoare.whoare import WhoAre


class Dominio(models.Model):
    nombre = models.CharField(max_length=240)
    zona = models.ForeignKey('zonas.Zona', on_delete=models.CASCADE, related_name='dominios', help_text="Lo que va al final y no es parte del dominio")
    registrante = models.ForeignKey('registrantes.Registrante', null=True, blank=True, on_delete=models.SET_NULL, related_name='dominios')
    data_updated = models.DateTimeField(null=True, blank=True, help_text='When this record was updated')

    registered = models.DateTimeField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    expire = models.DateTimeField(null=True, blank=True)
    
    extras = models.JSONField(null=True, blank=True)

    # fields to be deleted
    uid_anterior = models.IntegerField(default=0, help_text="to be deleted after migration")
    # 0 es no empezado, 1 es empezado, 2 es terminado OK
    changes_migrated = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.nombre}.{self.zona.nombre}'
        
    @classmethod
    def create_from_whois(cls, domain):
        from zonas.models import Zona
        from registrantes.models import Registrante
        from dnss.models import DNS

        wa = WhoAre()
        wa.load(domain)
        
        # wa.domain.registered datetime.datetime(2020, 5, 7, 10, 44, 4, 210977)
        # wa.domain.expire datetime.datetime(2021, 5, 7, 0, 0)
        # wa.registrant.name 'XXXX jose XXXXX'
        # wa.registrant.legal_uid '20XXXXXXXX9'
        # wa.dnss[0].name 'ns2.sedoparking.com'
        # wa.dnss[1].name 'ns1.sedoparking.com'
        
        zona = Zona.objects.get_or_create(nombre=wa.domain.zone)
        dominio = Dominio.objects.get_or_create(nombre=wa.domain.base_name, zona=zona)

        # TODO
        # for dns in wa.dnss:
        #     dns = DNS

        return dominio
        
class DNSDominio(models.Model):
    dominio = models.ForeignKey(Dominio, on_delete=models.RESTRICT, related_name='dnss')
    dns = models.ForeignKey('dnss.DNS', on_delete=models.RESTRICT, related_name='dominios')
    orden = models.IntegerField()
    
    class Meta:
        unique_together = (('dominio', 'dns', 'orden'), )