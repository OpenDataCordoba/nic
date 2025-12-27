"""
Archivo hecho completamente por Sonnet 3.7
"""
from django.test import TestCase, Client
from django.urls import reverse
from dnss.models import Empresa, DNS, EmpresaRegexDomain
from dominios.models import Dominio, DNSDominio
from registrantes.models import Registrante
from zonas.models import Zona


class HostingViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create test hosting company
        self.empresa = Empresa.objects.create(
            nombre="Test Hosting"
        )
        self.empresa_uid = self.empresa.uid

        # Create a regex for the company
        self.regex = EmpresaRegexDomain.objects.create(
            empresa=self.empresa,
            regex_dns="testdns\\.com"
        )

        # Create a DNS entry
        self.dns = DNS.objects.create(
            dominio="testdns.com",
            empresa_regex=self.regex
        )

        zona = Zona.objects.create(nombre="com")
        # uid like uuid.uuid4
        self.registrante = Registrante.objects.create(
            uid='123e4567-e89b-12d3-a456-426614174000',
            name="Test Registrante"
        ) 
        # Create a test domain using this DNS
        self.dominio = Dominio.objects.create(
            nombre="example",
            zona=zona,
            registrante=self.registrante,
        )
        DNSDominio.objects.create(
            dominio=self.dominio,
            dns=self.dns,
            orden=1,
        )

        self.url = reverse('hosting', kwargs={'uid': self.empresa_uid})

    def test_hosting_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/hosting/hosting.html')
        self.assertEqual(response.context['hosting'], self.empresa)
        self.assertIn('ultimos_dominios', response.context)
        self.assertIn('total_dominios', response.context)


class HostingsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create some test hosting companies
        self.empresa1 = Empresa.objects.create(nombre="Test Hosting 1")
        self.empresa2 = Empresa.objects.create(nombre="Test Hosting 2")

        # URLs
        self.url = reverse('hostings')

    def test_hostings_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/hosting/hostings.html')
        self.assertIn('hostings', response.context)
        self.assertIn('dominios_sin_dns', response.context)
        self.assertIn('huerfanos', response.context)
        self.assertEqual(response.context['value_is'], 'Dominios')


class Hostings30ViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create some test hosting companies
        self.empresa1 = Empresa.objects.create(nombre="Test Hosting 1")
        self.empresa2 = Empresa.objects.create(nombre="Test Hosting 2")

        # URLs
        self.url = reverse('hostings-30')

    def test_hostings30_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/hosting/hostings.html')
        self.assertIn('hostings', response.context)
        self.assertEqual(response.context['value_is'], 'Dominios (ult 30 días)')
        self.assertEqual(response.context['site_title'], 'Hostings mas usados (30 días)')


class DNSViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a DNS entry
        self.dns = DNS.objects.create(
            dominio="testdns.com"
        )
        self.dns_uid = self.dns.uid

        # Create a test domain using this DNS
        zona = Zona.objects.create(nombre="com")
        self.dominio = Dominio.objects.create(
            nombre="example",
            zona=zona,
        )
        DNSDominio.objects.create(
            dominio=self.dominio,
            dns=self.dns,
            orden=1,
        )

        self.url = reverse('dns', kwargs={'uid': self.dns_uid})

    def test_dns_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/hosting/dns.html')
        self.assertEqual(response.context['dns'], self.dns)
        self.assertIn('dominios', response.context)


class PerdidasViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('hostings-perdidas-30')

    def test_perdidas_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/hosting/perdidas.html')
        self.assertIn('perdidas', response.context)
        self.assertEqual(response.context['site_title'], 'Perdidas de clientes')
        self.assertEqual(response.context['site_description'], 'Perdidas de clientes por empresas de hosting')
