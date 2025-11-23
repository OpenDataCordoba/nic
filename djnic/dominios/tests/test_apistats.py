from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from dominios.models import Dominio, STATUS_DISPONIBLE
from zonas.models import Zona
from django.utils import timezone

class APIStatsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        permission = Permission.objects.get(
            codename='view_dominio',
            content_type__app_label='dominios',
            content_type__model='dominio'
        )
        self.user.user_permissions.add(permission)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.force_login(self.user)

        self.zona = Zona.objects.create(nombre='ar')
        self.dominio = Dominio.objects.create(
            nombre='test.ar',
            zona=self.zona,
            estado=STATUS_DISPONIBLE,
            registered=timezone.now(),
            expire=timezone.now()
        )
        self.anon_client = APIClient()

    def test_general_stats(self):
        url = '/api/v1/dominios/stats/general'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_priority_stats_anon(self):
        url = '/api/v1/dominios/stats/priority'
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_priority_stats_logged_in(self):
        url = '/api/v1/dominios/stats/priority'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_registrados_por_fecha_stats(self):
        url = '/api/v1/dominios/stats/registrados-por-fecha'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_vencimientos_por_fecha_stats(self):
        url = '/api/v1/dominios/stats/vencimientos-por-fecha'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
