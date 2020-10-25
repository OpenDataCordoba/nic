from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from zonas.models import Zona

import logging
logger = logging.getLogger(__name__)

class CambioDominioTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.all = []
        cls.zona = Zona.objects.create(nombre='ar')

    def create_domain(self, delta_updated, delta_readed, status=STATUS_NO_DISPONIBLE, delta_expire=None):

        if status == STATUS_DISPONIBLE:
            nombre = f'FU{delta_updated.days}R{delta_readed.days}'
        else:
            if delta_expire.days < 0:
                nombre = f'E{-delta_expire.days}U{delta_updated.days}R{delta_readed.days}'
            else:
                nombre = f'R{delta_expire.days}U{delta_updated.days}R{delta_readed.days}'

        # logger.info(f'Creating {nombre}')        
        dom = Dominio.objects.create(
            nombre=nombre,
            zona=self.zona,
            estado=status,
            expire=timezone.now() + delta_expire if status==STATUS_NO_DISPONIBLE else None,
            data_updated=timezone.now() - delta_updated,
            data_readed=timezone.now() - delta_readed)
        
        # calcupar la prioridad a estos dominios
        dom.calculate_priority()
        self.all.append(dom)
        return dom
        
    def test_priority_order(self):

        for u in range(0, 101, 10):
            for r in range(0, 101, 10):
                self.create_domain(status=STATUS_DISPONIBLE, delta_updated=timedelta(days=u), delta_readed=timedelta(days=r))
        
        for e in range(-30, 31, 10):
            for u in range(0, 101, 10):
                for r in range(0, r+1, 10):
                    self.create_domain(delta_expire=timedelta(days=e), delta_updated=timedelta(days=u), delta_readed=timedelta(days=r))

        # create some really bad ones
        # R1500U300R300
        self.create_domain(delta_expire=timedelta(days=1500), delta_updated=timedelta(days=300), delta_readed=timedelta(days=300))
        # E1500U300R300
        self.create_domain(delta_expire=timedelta(days=-1500), delta_updated=timedelta(days=300), delta_readed=timedelta(days=300))
        # FU300R300
        self.create_domain(status=STATUS_DISPONIBLE, delta_updated=timedelta(days=300), delta_readed=timedelta(days=300))

        # most importants
        # E60U300R10
        self.create_domain(delta_expire=timedelta(days=-60), delta_updated=timedelta(days=300), delta_readed=timedelta(days=10))
        # R5U300R380
        self.create_domain(delta_expire=timedelta(days=5), delta_updated=timedelta(days=300), delta_readed=timedelta(days=380))

        # ver en este contexto cuales son los prioritarios
        dominios = Dominio.objects.all().order_by('-priority_to_update')

        results = {}
        c = dominios.count()
        for dominio in dominios:
            results[dominio.nombre] = dominio.priority_to_update
            logger.info(f'{dominio.nombre} = {dominio.priority_to_update}')
            c -= 1

        # free, updated 30 days ago, different last readed date
        self.assertGreater(results['FU30R30'], results['FU30R20'])
        self.assertGreater(results['FU30R20'], results['FU30R10'])
        self.assertGreater(results['FU30R10'], results['FU30R0'])

        # free, readed 30 days ago, different last updated date
        self.assertGreater(results['FU30R30'], results['FU20R30'])
        self.assertGreater(results['FU20R30'], results['FU10R30'])
        self.assertGreater(results['FU10R30'], results['FU0R30'])
        
        # expired 30 days ago
        self.assertGreater(results['E30U30R30'], results['E30U30R20'])
        self.assertGreater(results['E30U30R20'], results['E30U30R10'])
        self.assertGreater(results['E30U30R10'], results['E30U30R0'])

        self.assertGreater(results['E30U30R30'], results['E30U20R30'])
        self.assertGreater(results['E30U20R30'], results['E30U10R30'])
        self.assertGreater(results['E30U10R30'], results['E30U0R30'])
        
        # registered, expire in 30 days ago
        self.assertGreater(results['R30U30R30'], results['R30U30R20'])
        self.assertGreater(results['R30U30R20'], results['R30U30R10'])
        self.assertGreater(results['R30U30R10'], results['R30U30R0'])

        self.assertGreater(results['R30U30R30'], results['R30U20R30'])
        self.assertGreater(results['R30U20R30'], results['R30U10R30'])
        self.assertGreater(results['R30U10R30'], results['R30U0R30'])
        
        # expired > registered
        self.assertGreater(results['E30U70R10'], results['R30U70R10'])
        self.assertGreater(results['E30U30R10'], results['R30U30R10'])

        # expired > free
        self.assertGreater(results['E30U70R10'], results['FU70R10'])
        self.assertGreater(results['E30U30R10'], results['FU30R10'])

        # registered > free
        self.assertGreater(results['R30U70R10'], results['FU70R10'])
        self.assertGreater(results['R30U30R10'], results['FU30R10'])

        # bad ones
        self.assertGreater(results['R30U70R10'], results['R1500U300R300'])
        self.assertGreater(results['R30U70R10'], results['E1500U300R300'])
        self.assertGreater(results['R30U70R20'], results['FU300R300'])
        
        # Important
        self.assertGreater(results['E60U300R10'], results['R5U300R380'])
        