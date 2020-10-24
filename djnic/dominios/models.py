from datetime import timedelta
import logging
import pytz
from django.db import models
from django.utils import timezone
from whoare.whoare import WhoAre
from whoare.exceptions import TooManyQueriesError
from cambios.models import CambiosDominio, CampoCambio
from zonas.models import Zona
from registrantes.models import Registrante
from dnss.models import DNS


STATUS_DISPONIBLE = 'disponible'
STATUS_NO_DISPONIBLE = 'no disponible'
logger = logging.getLogger(__name__)


class Dominio(models.Model):
    nombre = models.CharField(max_length=240, db_index=True, help_text='Nombre solo sin la zona')
    zona = models.ForeignKey('zonas.Zona', on_delete=models.CASCADE, related_name='dominios', help_text="Lo que va al final y no es parte del dominio")
    registrante = models.ForeignKey('registrantes.Registrante', null=True, blank=True, on_delete=models.SET_NULL, related_name='dominios')
    
    data_updated = models.DateTimeField(null=True, blank=True, help_text='When this record was updated')
    data_readed = models.DateTimeField(null=True, blank=True, help_text='When this record was readad (having changes or not)')
    
    estado = models.CharField(null=True, max_length=90, db_index=True)
    registered = models.DateTimeField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    expire = models.DateTimeField(null=True, blank=True)
    
    priority_to_update = models.IntegerField(default=0, help_text='How mamy important is to update this domain')
    next_update_priority = models.DateTimeField(default=timezone.now, help_text='Next time I need to update the "priority"')
    extras = models.JSONField(null=True, blank=True)

    # fields to be deleted
    uid_anterior = models.IntegerField(default=0, db_index=True, help_text="to be deleted after migration")
    # 0 es no empezado, 1 es empezado, 2 es terminado OK
    changes_migrated = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (('nombre', 'zona'), )
        
    def get_zoned_date(self, field):
        """ put a datetime in the rigth timezone before move to string """
        
        if field == 'registered':
            timefield = self.registered
        elif field == 'changed':
            timefield = self.changed
        elif field == 'expire':
            timefield = self.expire
        else:
            raise Exception('Bad field date')
        
        logger.info(f'Transforming date {timefield} {self.zona.tz}')
        return timezone.localtime(timefield, pytz.timezone(self.zona.tz))

    def full_domain(self):
        nombre = self.nombre if self.nombre is not None else ''
        zona = '' if self.zona is None else self.zona.nombre
        return f'{nombre}.{zona}'

    def __str__(self):
        return self.full_domain()
    
    def last_change(self):
        return self.cambios.order_by('-momento').first()
    
    @classmethod
    def add_from_whois(cls, domain, just_new=False, mock_from_txt_file=None):
        """ create or update a domain from WhoIs info
            Returns None if error or the domain object
            """
        
        logger.info(f'Adding from WhoIs {domain}')
        wa = WhoAre()
        domain_name, zone = wa.detect_zone(domain)
        zona, _ = Zona.objects.get_or_create(nombre=zone)

        if just_new:
            dominios = Dominio.objects.filter(nombre=domain_name, zona=zona)
            if dominios.count() > 0:
                if dominios[0].data_updated is not None:
                    return True
        
        try:
            wa.load(domain, mock_from_txt_file=mock_from_txt_file)
        except TooManyQueriesError:
            return None
        
        dominio, dominio_created = Dominio.objects.get_or_create(nombre=wa.domain.base_name, zona=zona)
        # create a domain after being sure we don't have any whoare errors
        logger.info(f' - Dominio {dominio} Created: {dominio_created}')
        
        return dominio.update_from_wa_object(wa, just_created=dominio_created)
            
    def update_from_wa_object(self, wa, just_created):
        """ Update a domain from a WhoAre object
            To use from external users and from local generation """
        
        self.data_readed = timezone.now()

        cambios = []
        # is already exist analyze and register changes
        if not just_created:
            cambios = self.apply_new_version(whoare_object=wa)
        else:
            self.data_updated = timezone.now()

        self.estado = STATUS_DISPONIBLE if wa.domain.is_free else STATUS_NO_DISPONIBLE

        if wa.registrant is not None:
            registrante, created = Registrante.objects.get_or_create(legal_uid=wa.registrant.legal_uid)
            registrante.name = wa.registrant.name
            registrante.legal_uid = wa.registrant.legal_uid
            registrante.created = wa.registrant.created
            registrante.changed = wa.registrant.changed
            registrante.save()
            logger.info(f' - Registrante {registrante} Created: {created}')
        
            self.registrante = registrante
    
        self.registered = wa.domain.registered
        self.changed = wa.domain.changed
        self.expire = wa.domain.expire

        self.save()

        orden = 1
        for ns in wa.dnss:
            new_dns, dns_created = DNS.objects.get_or_create(dominio=ns.name)
            
            # get previous DNS in this order
            previous = DNSDominio.objects.filter(dominio=self, orden=orden)
            if previous.count() > 0:
            
                dns_found = False
                for prev in previous:
                    if prev.dns != new_dns:
                        # delete all 
                        prev.delete()
                    else:
                        dns_found = True
                if not dns_found:
                    DNSDominio.objects.create(dominio=self, dns=new_dns, orden=orden)

            elif previous.count() == 0:    
                DNSDominio.objects.create(dominio=self, dns=new_dns, orden=orden)
                    
            orden += 1
        
        # delete exceding DNSs from previous version
        DNSDominio.objects.filter(dominio=self, orden__gt=len(wa.dnss)).delete()

        # volver a calcular su prioridad
        self.calculate_priority()
        return cambios

    def apply_new_version(self, whoare_object):
        """ Get a new version of domain, check differences and register changes """
        wa = whoare_object
        logger.info(f'Apply new version {self} {wa}')
        
        # ensure is the same
        assert self.nombre == wa.domain.base_name
        assert self.zona.nombre == wa.domain.zone

        cambios = []
        if self.estado == STATUS_NO_DISPONIBLE and wa.domain.is_free:
            cambios.append({"campo": "estado", "anterior": STATUS_NO_DISPONIBLE, "nuevo": STATUS_DISPONIBLE})
        elif self.estado == STATUS_DISPONIBLE and not wa.domain.is_free:
            cambios.append({"campo": "estado", "anterior": STATUS_DISPONIBLE, "nuevo": STATUS_NO_DISPONIBLE})
        
        r_val = '' if self.registered is None else self.get_zoned_date('registered').strftime("%Y-%m-%d %H:%M:%S")
        w_val = '' if wa.domain.registered is None else wa.domain.registered.strftime("%Y-%m-%d %H:%M:%S")    
        if r_val != w_val:
            cambios.append({"campo": "dominio_registered", "anterior": r_val, "nuevo": w_val})

        r_val = '' if self.changed is None else self.get_zoned_date('changed').strftime("%Y-%m-%d %H:%M:%S")
        w_val = '' if wa.domain.changed is None else wa.domain.changed.strftime("%Y-%m-%d %H:%M:%S")
        if r_val != w_val:
            cambios.append({"campo": "dominio_changed", "anterior": r_val, "nuevo": w_val})

        r_val = '' if self.expire is None else self.get_zoned_date('expire').strftime("%Y-%m-%d %H:%M:%S")
        w_val = '' if wa.domain.expire is None else wa.domain.expire.strftime("%Y-%m-%d %H:%M:%S")
        if r_val != w_val:
            cambios.append({"campo": "dominio_expire", "anterior": r_val, "nuevo": w_val})
        
        if self.registrante is not None:
            r_name = self.registrante.name
            r_legal_uid = self.registrante.legal_uid
            r_created = self.registrante.get_zoned_date('created', self.zona.tz).strftime("%Y-%m-%d %H:%M:%S")
            r_changed = self.registrante.get_zoned_date('changed', self.zona.tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            r_name, r_legal_uid, r_created, r_changed = ('', '', '', '') 

        if wa.registrant is not None:
            w_name = wa.registrant.name
            w_legal_uid = wa.registrant.legal_uid
            w_created = wa.registrant.created.strftime("%Y-%m-%d %H:%M:%S")
            w_changed = wa.registrant.changed.strftime("%Y-%m-%d %H:%M:%S")
        else:
            w_name, w_legal_uid, w_created, w_changed = ('', '', '', '') 
        
        if r_name != w_name:
            cambios.append({"campo": "registrant_name", "anterior": r_name, "nuevo": w_name})
        
        if r_legal_uid != w_legal_uid:
            cambios.append({"campo": "registrant_legal_uid", "anterior": r_legal_uid, "nuevo": w_legal_uid})
        
        if r_created != w_created:
            cambios.append({"campo": "registrant_created", "anterior": r_created, "nuevo": w_created})
        
        if r_changed != w_changed:
            cambios.append({"campo": "registrant_changed", "anterior": r_changed, "nuevo": w_changed})
        
        r_dnss = [d.dns.dominio for d in self.dnss.all().order_by('orden')]
        w_dnss = [d.name for d in wa.dnss]
        
        max_len = max(len(r_dnss), len(w_dnss))
        for n in range(max_len):
            r_val = '' if (n+1) > len(r_dnss) else r_dnss[n]
            w_val = '' if (n+1) > len(w_dnss) else w_dnss[n]

            if r_val != w_val:
                cambios.append({"campo": f"DNS{n+1}", "anterior": r_val, "nuevo": w_val})

        have_changes = len(cambios) > 0
        main_change = CambiosDominio.objects.create(dominio=self, momento=timezone.now(), have_changes=have_changes)

        if have_changes:
            
            for cambio in cambios:
                logger.info(f" - CAMBIO {cambio['campo']} FROM {cambio['anterior']} TO {cambio['nuevo']}")
        
                CampoCambio.objects.create(
                    cambio=main_change,
                    campo=cambio['campo'],
                    anterior=cambio['anterior'],
                    nuevo=cambio['nuevo'])
            
            self.data_updated = timezone.now()
        else:
            logger.info(f' - SIN CAMBIOS {self}')
        
        return cambios
        
    def calculate_priority(self):
        """ We need a way to know how to use resources
            We can't update all domains every day.

            Define a priority value and a next_update date for this domain
            """
        logger.info(f'Calculating priority for {self}')
        day_seconds = 86400
        
        # days measures
        updated_since = 0 if self.data_updated is None else int((timezone.now() - self.data_updated).total_seconds() / day_seconds)
        readed_since = 0 if self.data_readed is None else int((timezone.now() - self.data_readed).total_seconds() / day_seconds)
        expired_since = 0 if self.expire is None else int((timezone.now() - self.expire).total_seconds() / day_seconds)  
        
        if self.zona.nombre == 'ar' or self.zona.nombre.endswith('.ar'):
            from dominios.priority.ar import calculate_priority
            priority = calculate_priority(expired_since, readed_since, updated_since, self.estado)
        else:
            raise Exception('Unknown domain')

        self.priority_to_update = priority
        self.next_update_priority = timezone.now() + timedelta(days=7)
        self.save()
        return self
        
class DNSDominio(models.Model):
    dominio = models.ForeignKey(Dominio, on_delete=models.RESTRICT, related_name='dnss')
    dns = models.ForeignKey('dnss.DNS', on_delete=models.RESTRICT, related_name='dominios')
    orden = models.IntegerField()
    
    class Meta:
        unique_together = (('dominio', 'dns', 'orden'), )
