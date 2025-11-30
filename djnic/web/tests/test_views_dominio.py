from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from cambios.models import CambiosDominio, CampoCambio
from zonas.models import Zona
from django.utils import timezone
from datetime import timedelta


class DominioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.zona = Zona.objects.create(nombre="ar")
        self.dominio = Dominio.objects.create(
            nombre="testdomain",
            zona=self.zona,
            estado=STATUS_DISPONIBLE
        )
        self.url = reverse('dominio', kwargs={'uid': self.dominio.uid})

    def test_dominio_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominio.html')
        self.assertEqual(response.context['dominio'], self.dominio)
        self.assertEqual(response.context['estado'], 'Disponible')


class UltimosCaidosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('ultimos-caidos')
        self.zona = Zona.objects.create(nombre="ar")
        # Create 12 "dominios caidos" (domains that changed from NO_DISPONIBLE to DISPONIBLE)
        for i in range(12):
            dominio = Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_DISPONIBLE,
                data_updated=timezone.now() - timedelta(hours=i)
            )
            # Create a CambiosDominio (change) record for this domain
            cambio = CambiosDominio.objects.create(
                dominio=dominio,
                momento=timezone.now() - timedelta(hours=i),
                have_changes=True
            )
            # Create a CampoCambio (field change) tracking the estado change
            CampoCambio.objects.create(
                cambio=cambio,
                campo='estado',
                anterior=STATUS_NO_DISPONIBLE,
                nuevo=STATUS_DISPONIBLE
            )

    def test_ultimos_caidos_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/ultimos-caidos.html')
        self.assertIn('ultimos_caidos', response.context)
        # Unauthenticated user sees limited results
        self.assertLessEqual(len(response.context['ultimos_caidos']), 5)

    def test_ultimos_caidos_view_authenticated(self):
        User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Authenticated user sees all results
        self.assertEqual(len(response.context['ultimos_caidos']), 12)


class UltimosRegistradosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('ultimos-registrados')
        self.zona = Zona.objects.create(nombre="ar")
        # Create some domains
        for i in range(6):
            Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                registered=timezone.now()
            )

    def test_ultimos_registrados_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/ultimos-registrados.html')
        self.assertIn('ultimos_registrados', response.context)
        # Unauthenticated user sees limited results
        self.assertLessEqual(len(response.context['ultimos_registrados']), 5)


class JudicializadosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('judicializados')
        self.zona = Zona.objects.create(nombre="ar")
        # Create some domains
        for i in range(6):
            Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                expire=timezone.now() - timedelta(days=10),  # Expired
                data_updated=timezone.now()
            )

    def test_judicializados_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/judicializados.html')
        self.assertIn('dominios', response.context)


class DominiosAntiguosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('dominios-antiguos')
        self.zona = Zona.objects.create(nombre="ar")
        # Create some domains
        for i in range(6):
            Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                registered=timezone.now() - timedelta(days=365*10)
            )

    def test_dominios_antiguos_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/antiguos.html')
        self.assertIn('dominios', response.context)


class DominiosVencimientoLargoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('dominios-futuros')
        self.zona = Zona.objects.create(nombre="ar")
        # Create some domains
        for i in range(6):
            Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                expire=timezone.now() + timedelta(days=365*5)
            )

    def test_dominios_futuros_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/futuros.html')
        self.assertIn('dominios', response.context)


class PorCaerViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('por-caer')
        self.zona = Zona.objects.create(nombre="ar")
        # Create some domains
        for i in range(6):
            Dominio.objects.create(
                nombre=f"test{i}",
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                expire=timezone.now() - timedelta(days=1)
            )

    def test_por_caer_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/por-caer.html')
        self.assertIn('por_caer', response.context)
