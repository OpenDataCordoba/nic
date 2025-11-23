from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from dnss.models import Empresa, DNS
from dominios.models import Dominio, STATUS_NO_DISPONIBLE
from zonas.models import Zona

class CsvEmpresasViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client.login(username='testuser', password='password')
        self.url = reverse('csv-empresas')
        Empresa.objects.create(nombre="Test Hosting")

    def test_csv_empresas_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="empresas.csv"', response['Content-Disposition'])

    def test_csv_empresas_view_anon(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 204)

class CsvDnssViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client.login(username='testuser', password='password')
        self.url = reverse('csv-dnss')
        DNS.objects.create(dominio="ns1.example.com")

    def test_csv_dnss_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="dnss.csv"', response['Content-Disposition'])

    def test_csv_dnss_view_anon(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 204)

class CsvDominiosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client.login(username='testuser', password='password')
        self.url = reverse('csv-dominios')
        zona = Zona.objects.create(nombre="ar")
        Dominio.objects.create(
            nombre="testdomain",
            zona=zona,
            estado=STATUS_NO_DISPONIBLE
        )

    def test_csv_dominios_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="dominios.csv"', response['Content-Disposition'])

    def test_csv_dominios_view_anon(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 204)
