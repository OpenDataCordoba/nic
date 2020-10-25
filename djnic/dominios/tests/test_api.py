from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.test import TestCase
from dominios.models import Dominio, STATUS_DISPONIBLE
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
        cls.dom = Dominio.objects.create(
            nombre='test.ar',
            zona=cls.zona,
            estado=STATUS_DISPONIBLE)

    def test_api_dominios(self):
        
        ep = '/api/v1/dominios/dominio/'
            
        resp = self.anon_client.get(ep)
        self.assertEqual(resp.status_code, 401)

        resp = self.regular_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_regular_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_admin_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        # TODO prepare serilizer
        # data = {'nombre': 'lala', 'zona': self.zona.id}
        # resp = self.anon_client.post(ep, data)
        # self.assertEqual(resp.status_code, 401)
        
    def test_api_dominio(self):
        
        ep = f'/api/v1/dominios/dominio/{self.dom.id}/'
            
        resp = self.anon_client.get(ep)
        self.assertEqual(resp.status_code, 401)

        resp = self.regular_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_regular_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_admin_client.get(ep)
        self.assertEqual(resp.status_code, 200)
    
    def test_api_next_priority(self):
        
        ep = '/api/v1/dominios/next-priority/'
            
        resp = self.anon_client.get(ep)
        self.assertEqual(resp.status_code, 401)

        resp = self.regular_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_regular_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.admin_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        
        resp = self.tokened_admin_client.get(ep)
        self.assertEqual(resp.status_code, 200)

    def test_api_lists(self):
        
        endpoints = [
            '/api/v1/dominios/ultimos-caidos/',
            '/api/v1/dominios/next-priority/',
            '/api/v1/dominios/ultimos-renovados/',
            '/api/v1/dominios/ultimos-transpasados/',
            '/api/v1/dominios/ultimos-cambio-dns/'
        ]

        for ep in endpoints:
            
            resp = self.anon_client.get(ep)
            self.assertEqual(resp.status_code, 401)

            resp = self.regular_user_client.get(ep)
            self.assertEqual(resp.status_code, 200)
            
            resp = self.tokened_regular_client.get(ep)
            self.assertEqual(resp.status_code, 200)
            
            resp = self.admin_user_client.get(ep)
            self.assertEqual(resp.status_code, 200)
            
            resp = self.tokened_admin_client.get(ep)
            self.assertEqual(resp.status_code, 200)
            