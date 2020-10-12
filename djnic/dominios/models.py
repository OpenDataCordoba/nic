from django.db import models
import whois

class Dominio(models.Model):
    nombre = models.CharField(max_length=240)
    zona = models.ForeignKey('zonas.Zona', on_delete=models.CASCADE, help_text="Lo que va al final y no es parte del dominio")
    # registrante = models.ForeignKey('registrantes.Registrante', null=True, blank=True, on_delete=models.SET_NULL)
    extras = models.JSONField(null=True, blank=True)


    @classmethod
    def create_from_whois(cls, domain, zone):
        from zonas.models import Zona
        zona = Zona.objects.get_or_create(nombre=zone)
        full_domain = f'{domain}.{zona.nombre}'
        wdomain = whois.query(full_domain)

        assert wdomain.name == full_domain


        """
        

        self.registrar = data['registrar'][0].strip()
        self.registrant_country = data['registrant_country'][0].strip()
        self.creation_date = str_to_date(data['creation_date'][0])
        self.expiration_date = str_to_date(data['expiration_date'][0])
        self.last_updated = str_to_date(data['updated_date'][0])
        self.status = data['status'][0].strip()
        self.statuses = list(set([s.strip() for s in data['status']])) # list(set(...))) to deduplicate
        self.dnssec = BOOLEAN
        """