"""
Archivo hecho completamente por Sonnet 3.7
"""
from django.test import TestCase, Client
from django.urls import reverse
from registrantes.models import Registrante, TagForRegistrante
import uuid


class RegistranteViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a test registrante
        self.test_uid = str(uuid.uuid4())
        self.registrante = Registrante.objects.create(
            uid=self.test_uid,
            name="Test Registrante"
        )
        self.url = reverse('registrante', kwargs={'uid': self.test_uid})

    def test_registrante_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/registrante.html')


class RegistrantesAntiguosViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('registrantes-antiguos')

    def test_registrantes_antiguos_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/registrantes/antiguos.html')


class MayoresRegistrantesViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('mayores-registrantes')

    def test_mayores_registrantes_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/registrantes/mayores.html')


class RubrosViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('rubros')

    def test_rubros_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/registrantes/rubros.html')


class RubroViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a test tag/rubro
        self.test_uid = str(uuid.uuid4())
        self.tag = TagForRegistrante.objects.create(
            uid=self.test_uid,
            nombre="Test Tag",
        )
        self.url = reverse('rubro', kwargs={'uid': self.test_uid})

    def test_rubro_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/registrantes/rubro.html')

    def test_rubro_context_data(self):
        response = self.client.get(self.url)
        self.assertIn('ultimos_registrados', response.context)
        self.assertIn('mayores_registrantes', response.context)
        self.assertEqual(response.context['site_title'], f'Rubro o Tag {self.tag.nombre}')
