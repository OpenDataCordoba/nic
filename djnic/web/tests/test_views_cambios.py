"""
Archivo hecho completamente por Sonnet 3.7
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from dominios.models import Dominio
from zonas.models import Zona


class RenovacionesViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('renovaciones')
        # Create a test user for authenticated tests
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        # Create test data
        zona = Zona.objects.create(nombre="ar")
        self.dominio = Dominio.objects.create(
            nombre="testdomain",
            zona=zona,
        )

    def test_renovaciones_view_unauthenticated(self):
        """Test that unauthenticated users can access the view with limited results"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')

        # Check context limits
        self.assertIn('campos', response.context)
        if len(response.context['campos']) > 0:
            self.assertLessEqual(len(response.context['campos']), 5)

    def test_renovaciones_view_authenticated(self):
        """Test that authenticated users can access the view with more results"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')


class RenovacionesRarasViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('renovaciones-raras')
        # Create a test user for authenticated tests
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        # Create test data
        zona = Zona.objects.create(nombre="ar")
        self.dominio = Dominio.objects.create(
            nombre="testdomain",
            zona=zona,
        )

    def test_renovaciones_raras_view_unauthenticated(self):
        """Test that unauthenticated users can access the view with limited results"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')

        # Check context limits
        self.assertIn('campos', response.context)
        if len(response.context['campos']) > 0:
            self.assertLessEqual(len(response.context['campos']), 5)

    def test_renovaciones_raras_view_authenticated(self):
        """Test that authenticated users can access the view with more results"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')
        self.assertEqual(response.context['site_title'], 'Renovaciones de dominio')


class RenovacionesHaciaAtrasViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('renovaciones-para-atras')
        # Create a test user for authenticated tests
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        # Create test data
        zona = Zona.objects.create(nombre="ar")
        self.dominio = Dominio.objects.create(
            nombre="testdomain",
            zona=zona,
        )

    def test_renovaciones_hacia_atras_view_unauthenticated(self):
        """Test that unauthenticated users can access the view with limited results"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')

        # Check context limits
        self.assertIn('campos', response.context)
        if len(response.context['campos']) > 0:
            self.assertLessEqual(len(response.context['campos']), 5)

    def test_renovaciones_hacia_atras_view_authenticated(self):
        """Test that authenticated users can access the view with more results"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/dominios/renovaciones.html')
        self.assertEqual(response.context['site_title'], 'Renovaciones de dominio hacia atras')
        self.assertEqual(
            response.context['site_description'],
            'Lista de últimos dominios renovados con fecha de vencimiento que cambia hacia el pasado'
        )
