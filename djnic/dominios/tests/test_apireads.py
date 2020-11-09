from datetime import datetime, timedelta
import json
import requests
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase, LiveServerTestCase
from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from zonas.models import Zona


class APIDominioTestCase(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.anon_client = APIClient()
        cls.anon_client.credentials()
        cls.user = User.objects.create_user('john', 'jhon@lala.com', 'john')
        cls.regular_user_client = APIClient()
        cls.regular_user_client.login(username='john', password='john')

        cls.regular_user_token = Token.objects.create(user=cls.user)
        cls.tokened_regular_client = APIClient()
        cls.tokened_regular_client.credentials(HTTP_AUTHORIZATION='Token ' + cls.regular_user_token.key)
                
        cls.admin_user = User.objects.create_user('admin', 'admin@lala.com', 'admin', is_staff=True, is_superuser=True)
        cls.admin_user_client = APIClient()
        cls.admin_user_client.login(username='admin', password='admin')
        
        cls.admin_user_token = Token.objects.create(user=cls.admin_user)
        cls.tokened_admin_client = APIClient()
        cls.tokened_admin_client.credentials(HTTP_AUTHORIZATION='Token ' + cls.admin_user_token.key)

        cls.zona = Zona.objects.create(nombre='ar')
        

    def test_api_readings(self):
        
        ep = '/api/v1/dominios/stats/reading'
        
        resp = self.anon_client.get(ep)
        self.assertEqual(resp.status_code, 302)  # redirect to login

        resp = self.regular_user_client.get(ep)
        self.assertEqual(resp.status_code, 403)
        
        resp = self.tokened_regular_client.get(ep)
        self.assertEqual(resp.status_code, 302)
        
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data['data']['total'], 0)
        
        resp = self.tokened_admin_client.get(ep)
        self.assertEqual(resp.status_code, 302)  # redirige por que es un vista django que no ve los token en los headers

        hoy = timezone.now()
        for n in range(0, 10):

            Dominio.objects.create(
                nombre=f'test1-{n}.ar',
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                data_readed= hoy - timedelta(days=n),
                expire=hoy - timedelta(days=n)
                )
            
            Dominio.objects.create(
                nombre=f'test2-{n}.ar',
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                data_readed=hoy - timedelta(days=2*n),
                expire=hoy - timedelta(days=n)
                )
        
            Dominio.objects.create(
                nombre=f'test3-{n}.ar',
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                data_readed=hoy - timedelta(days=2 * n),
                expire=hoy + timedelta(days=n)
                )
            
            Dominio.objects.create(
                nombre=f'test4-{n}.ar',
                zona=self.zona,
                estado=STATUS_NO_DISPONIBLE,
                data_readed=hoy - timedelta(days=3 * n),
                expire=hoy + timedelta(days=n)
                )
        
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data['data']['total'], 40)
        
        def check(days_ago, read_since_days):
            dia = (hoy - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            print(f"DATES {days_ago} {dia} = {data['data']['dates'][dia]}")
            return data['data']['dates'][dia][str(read_since_days)]

        self.assertEqual(check(0, 0), 4)
        self.assertEqual(check(1, 1), 1)
        self.assertEqual(check(1, 2), 1)
        self.assertEqual(check(2, 2), 1)
        self.assertEqual(check(2, 4), 1)
        self.assertEqual(check(3, 3), 1)
        self.assertEqual(check(3, '5-10'), 1)
        
        ep = '/api/v1/dominios/stats/reading/3/3'
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(data['data']['total'], 14)
        