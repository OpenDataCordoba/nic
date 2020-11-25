from datetime import timedelta
import logging
import random
from time import sleep
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dominios.models import Dominio, STATUS_NO_DISPONIBLE
from zonas.models import GrupoZona, Zona, ZonaEnGrupo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Crear dominios para pruebas locales'

    # def add_arguments(self, parser):
    #     parser.add_argument('--sleep', nargs='?', type=int, default=41)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"Creating groups"))
        
        grupo_ar, created = GrupoZona.objects.get_or_create(nombre='Argentina', published=True)
        grupo_uy, created = GrupoZona.objects.get_or_create(nombre='Uruguay', published=True)
        grupo_cl, created = GrupoZona.objects.get_or_create(nombre='Chile', published=True)

        zona_ar,created = Zona.objects.get_or_create(nombre='ar')
        ZonaEnGrupo.objects.get_or_create(zona=zona_ar, grupo=grupo_ar, published=True)

        zona_gob_ar,created = Zona.objects.get_or_create(nombre='gob.ar')
        ZonaEnGrupo.objects.get_or_create(zona=zona_gob_ar, grupo=grupo_ar, published=True)

        zona_cl, created = Zona.objects.get_or_create(nombre='cl')
        ZonaEnGrupo.objects.get_or_create(zona=zona_cl, grupo=grupo_cl, published=True)

        zona_uy, created = Zona.objects.get_or_create(nombre='uy')
        ZonaEnGrupo.objects.get_or_create(zona=zona_uy, grupo=grupo_uy, published=True)

        zona_com_uy, created = Zona.objects.get_or_create(nombre='com.uy')
        ZonaEnGrupo.objects.get_or_create(zona=zona_com_uy, grupo=grupo_uy, published=True)

        zonas = [zona_ar, zona_cl, zona_com_uy, zona_gob_ar, zona_uy]

        hoy = timezone.now()
        for n in range(0, 5000):
            for zona in zonas:
                dom, created = Dominio.objects.get_or_create(nombre=f'test-{n}',zona=zona)
                dom.estado=STATUS_NO_DISPONIBLE
                dom.data_readed= hoy - timedelta(days=random.randint(1, 90))
                dom.data_updated= hoy - timedelta(days=random.randint(1, 60))
                dom.expire=hoy + timedelta(days=random.randint(1, 90))
                dom.save()

        self.stdout.write(self.style.SUCCESS(f"Finished"))
        