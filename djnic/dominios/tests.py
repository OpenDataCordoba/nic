from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from zonas.models import Zona


class CambioDominioTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.all = []
        cls.zona = Zona.objects.create(nombre='ar')

    def create_domain(self, name, delta_updated, status=STATUS_NO_DISPONIBLE, delta_expire=None):
        dom = Dominio.objects.create(
            nombre=name,
            zona=self.zona,
            estado=status,
            expire=timezone.now() + delta_expire if status==STATUS_NO_DISPONIBLE else None,
            data_updated=timezone.now() - delta_updated)
        
        self.all.append(dom)
        return dom
        
        
    def test_priority_order(self):

        self.create_domain(name='f10', status=STATUS_DISPONIBLE, delta_updated=timedelta(days=10))
        self.create_domain(name='f30', status=STATUS_DISPONIBLE, delta_updated=timedelta(days=30))
        self.create_domain(name='f60', status=STATUS_DISPONIBLE, delta_updated=timedelta(days=60))
        self.create_domain(name='f100', status=STATUS_DISPONIBLE, delta_updated=timedelta(days=100))

        self.create_domain(name='p50p5', delta_expire=timedelta(days=50), delta_updated=timedelta(days=150))
        self.create_domain(name='p50p15', delta_expire=timedelta(days=50), delta_updated=timedelta(days=120))
        self.create_domain(name='p50p1', delta_expire=timedelta(days=50), delta_updated=timedelta(days=90))
        
        self.create_domain(name='p30p90', delta_expire=timedelta(days=30), delta_updated=timedelta(days=90))
        self.create_domain(name='p30p5', delta_expire=timedelta(days=30), delta_updated=timedelta(days=5))
        self.create_domain(name='p30p15', delta_expire=timedelta(days=30), delta_updated=timedelta(days=15))
        self.create_domain(name='p30p1', delta_expire=timedelta(days=30), delta_updated=timedelta(days=1))
        
        self.create_domain(name='p20p90', delta_expire=timedelta(days=20), delta_updated=timedelta(days=90))
        self.create_domain(name='p20p5', delta_expire=timedelta(days=20), delta_updated=timedelta(days=5))
        self.create_domain(name='p20p15', delta_expire=timedelta(days=20), delta_updated=timedelta(days=15))
        self.create_domain(name='p20p1', delta_expire=timedelta(days=20), delta_updated=timedelta(days=1))

        self.create_domain(name='p10p90', delta_expire=timedelta(days=10), delta_updated=timedelta(days=90))
        self.create_domain(name='p10p60', delta_expire=timedelta(days=10), delta_updated=timedelta(days=60))
        self.create_domain(name='p10p5', delta_expire=timedelta(days=10), delta_updated=timedelta(days=5))
        self.create_domain(name='p10p15', delta_expire=timedelta(days=10), delta_updated=timedelta(days=15))
        self.create_domain(name='p10p1', delta_expire=timedelta(days=10), delta_updated=timedelta(days=1))
        
        self.create_domain(name='p1p90', delta_expire=timedelta(days=1), delta_updated=timedelta(days=90))
        self.create_domain(name='p1p60', delta_expire=timedelta(days=1), delta_updated=timedelta(days=60))
        self.create_domain(name='p1p5', delta_expire=timedelta(days=1), delta_updated=timedelta(days=5))
        self.create_domain(name='p1p15', delta_expire=timedelta(days=1), delta_updated=timedelta(days=15))
        self.create_domain(name='p1p1', delta_expire=timedelta(days=1), delta_updated=timedelta(days=1))
        
        self.create_domain(name='m1p90', delta_expire=-timedelta(days=1), delta_updated=timedelta(days=90))
        self.create_domain(name='m1p60', delta_expire=-timedelta(days=1), delta_updated=timedelta(days=60))
        self.create_domain(name='m1p5', delta_expire=-timedelta(days=1), delta_updated=timedelta(days=5))
        self.create_domain(name='m1p15', delta_expire=-timedelta(days=1), delta_updated=timedelta(days=15))
        self.create_domain(name='m1p1', delta_expire=-timedelta(days=1), delta_updated=timedelta(days=1))
        
        self.create_domain(name='m10p90', delta_expire=-timedelta(days=10), delta_updated=timedelta(days=90))
        self.create_domain(name='m10p60', delta_expire=-timedelta(days=10), delta_updated=timedelta(days=60))
        self.create_domain(name='m10p5', delta_expire=-timedelta(days=10), delta_updated=timedelta(days=5))
        self.create_domain(name='m10p15', delta_expire=-timedelta(days=10), delta_updated=timedelta(days=15))
        self.create_domain(name='m10p1', delta_expire=-timedelta(days=10), delta_updated=timedelta(days=1))
        
        self.create_domain(name='m30p90', delta_expire=-timedelta(days=30), delta_updated=timedelta(days=90))
        self.create_domain(name='m30p60', delta_expire=-timedelta(days=30), delta_updated=timedelta(days=60))
        self.create_domain(name='m30p5', delta_expire=-timedelta(days=30), delta_updated=timedelta(days=5))
        self.create_domain(name='m30p15', delta_expire=-timedelta(days=30), delta_updated=timedelta(days=15))
        self.create_domain(name='m30p1', delta_expire=-timedelta(days=30), delta_updated=timedelta(days=1))
        
        self.create_domain(name='m80p90', delta_expire=-timedelta(days=80), delta_updated=timedelta(days=90))
        self.create_domain(name='m80p60', delta_expire=-timedelta(days=80), delta_updated=timedelta(days=60))
        self.create_domain(name='m80p5', delta_expire=-timedelta(days=80), delta_updated=timedelta(days=5))
        self.create_domain(name='m80p15', delta_expire=-timedelta(days=80), delta_updated=timedelta(days=15))
        self.create_domain(name='m80p1', delta_expire=-timedelta(days=80), delta_updated=timedelta(days=1))
        
        self.create_domain(name='m100p90', delta_expire=-timedelta(days=100), delta_updated=timedelta(days=120))
        self.create_domain(name='m100p60', delta_expire=-timedelta(days=100), delta_updated=timedelta(days=60))
        self.create_domain(name='m100p5', delta_expire=-timedelta(days=100), delta_updated=timedelta(days=5))
        self.create_domain(name='m100p15', delta_expire=-timedelta(days=100), delta_updated=timedelta(days=15))
        self.create_domain(name='m100p1', delta_expire=-timedelta(days=100), delta_updated=timedelta(days=1))
        
        for dominio in self.all:
            dominio.calculate_priority()

        # ver en este contexto cuales son los prioritarios
        dominios = Dominio.objects.all().order_by('-priority_to_update')

        for dominio in dominios:
            print(dominio.nombre)

        