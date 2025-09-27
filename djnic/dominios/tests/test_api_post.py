import json
import requests
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase
from dominios.models import Dominio, STATUS_DISPONIBLE
from zonas.models import Zona


class APIDominioTestCase(LiveServerTestCase):

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


    def test_post_new_domain(self):

        ep = f'{self.live_server_url}/api/v1/dominios/dominio/update_from_whoare/'
        test_dict = {
            "domain": {
                "base_name": 'fernet',
                "zone": 'com.ar',
                "is_free": False,
                "registered": "2020-03-19 09:11:31.00000 +0300",
                "changed": "2020-03-19 09:11:30.00000 +0300",
                "expire": "2020-03-19 09:11:29.00000 +0300"
                },
            "registrant": {
                "name": "Jhon Perez",
                "legal_uid": "98798798798",
                "created": "2020-03-19 09:11:28.00000 +0300",
                "changed": "2020-03-19 09:11:27.00000 +0300"
            },
            "dnss": ['ns2.sedoparking.com', 'ns1.sedoparking.com']
        }
        str_data = json.dumps(test_dict)
        final = {'domain': str_data}

        resp = requests.post(ep, data=final)
        self.assertEqual(resp.status_code, 401)

        headers = {'Authorization': f'Token {self.regular_user_token.key}'}
        resp = requests.post(ep, data=final, headers=headers)
        self.assertEqual(resp.status_code, 403)

        headers = {'Authorization': f'Token {self.admin_user_token.key}'}
        resp = requests.post(ep, data=final, headers=headers)
        # missing whoare version
        self.assertEqual(resp.status_code, 400)

        test_dict['whoare_version'] = '0.1.42'
        str_data = json.dumps(test_dict)
        final = {'domain': str_data}
        resp = requests.post(ep, data=final, headers=headers)
        self.assertEqual(resp.status_code, 200)

