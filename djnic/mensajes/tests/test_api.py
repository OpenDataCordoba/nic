from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.test import TestCase
from mensajes.models import MensajeDestinado, Mensaje


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

        cls.user2 = User.objects.create_user('juan', 'jhon2@lala.com', 'juan')
        cls.regular_user_client2 = APIClient()
        cls.regular_user_client2.login(username='juan', password='juan')
        cls.regular_user_token2 = Token.objects.create(user=cls.user2)
        cls.tokened_regular_client2 = APIClient()
        cls.tokened_regular_client2.credentials(HTTP_AUTHORIZATION='Token ' + cls.regular_user_token2.key)

        users = [cls.user, cls.user2]

        for user in users:
            msg1 = Mensaje.objects.create(titulo=f'Unreaded {user.username}', texto='Hi unread')
            msg2 = Mensaje.objects.create(titulo=f'Readed {user.username}', texto='Hi readed')
            msg3 = Mensaje.objects.create(titulo=f'Deleted {user.username}', texto='Hi deleted')

            MensajeDestinado.objects.create(mensaje=msg1, destinatario=user)
            MensajeDestinado.objects.create(mensaje=msg2, destinatario=user, estado=MensajeDestinado.READED)
            MensajeDestinado.objects.create(mensaje=msg3, destinatario=user, estado=MensajeDestinado.DELETED)

    def test_api_read_lists(self):
        # API read messages list
        ep = '/api/v1/mensajes/mensaje/'

        resp = self.anon_client.get(ep)
        self.assertEqual(resp.status_code, 200)
        messages = resp.json()
        # there is no messages
        self.assertEqual(0, messages['count'])

        # User 1 ==========
        resp = self.regular_user_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        messages = resp.json()
        for message in messages['results']:
            self.assertIn(self.user.username, message['mensaje']['titulo'])
            self.assertEqual(self.user.id, message['destinatario'])
            self.assertNotIn('Deleted', message['mensaje']['titulo'])

        resp = self.tokened_regular_client.get(ep)
        self.assertEqual(resp.status_code, 200)

        messages = resp.json()
        for message in messages['results']:
            self.assertIn(self.user.username, message['mensaje']['titulo'])
            self.assertEqual(self.user.id, message['destinatario'])
            self.assertNotIn('Deleted', message['mensaje']['titulo'])
        
        # User 2 ==========
        resp = self.regular_user_client2.get(ep)
        self.assertEqual(resp.status_code, 200)

        messages = resp.json()
        for message in messages['results']:
            self.assertIn(self.user2.username, message['mensaje']['titulo'])
            self.assertEqual(self.user2.id, message['destinatario'])
            self.assertNotIn('Deleted', message['mensaje']['titulo'])

        resp = self.tokened_regular_client2.get(ep)
        self.assertEqual(resp.status_code, 200)

        messages = resp.json()
        for message in messages['results']:
            self.assertIn(self.user2.username, message['mensaje']['titulo'])
            self.assertEqual(self.user2.id, message['destinatario'])
            self.assertNotIn('Deleted', message['mensaje']['titulo'])

    def test_api_read_one(self):
        # read one message

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Anon 404
            resp = self.anon_client.get(ep)
            self.assertEqual(resp.status_code, 404)
            # Self user OK if not deleted
            resp = self.regular_user_client.get(ep)
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.regular_user_client2.get(ep)
            self.assertEqual(resp.status_code, 404)

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user2)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Anon 404
            resp = self.anon_client.get(ep)
            self.assertEqual(resp.status_code, 404)
            # Self user OK if not deleted
            resp = self.regular_user_client2.get(ep)
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.regular_user_client.get(ep)
            self.assertEqual(resp.status_code, 404)

        # Tokened clients
        msg_user = MensajeDestinado.objects.filter(destinatario=self.user)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Self user OK if not deleted
            resp = self.tokened_regular_client.get(ep)
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.tokened_regular_client2.get(ep)
            self.assertEqual(resp.status_code, 404)

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user2)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Self user OK if not deleted
            resp = self.tokened_regular_client2.get(ep)
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.tokened_regular_client.get(ep)
            self.assertEqual(resp.status_code, 404)

    def test_api_delete(self):
        # update status message

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Anon 404
            resp = self.anon_client.delete(ep)
            self.assertEqual(resp.status_code, 404)
            # Self user OK
            if msg.estado != MensajeDestinado.DELETED:
                resp = self.regular_user_client.delete(ep)
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(MensajeDestinado.objects.get(pk=msg.id).estado, MensajeDestinado.DELETED)
            # Other user 404
            resp = self.regular_user_client2.delete(ep)
            self.assertEqual(resp.status_code, 404)

    def test_api_patch(self):
        # update status message

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Anon 404
            resp = self.anon_client.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)
            # Self user OK
            resp = self.regular_user_client.patch(ep, {'estado': MensajeDestinado.READED})
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.regular_user_client2.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)
            # Self user bad estado
            resp = self.regular_user_client.patch(ep, {'estado': '9999999'})
            self.assertEqual(resp.status_code, 400)

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user2)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Anon 404
            resp = self.anon_client.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)
            # Self user OK
            resp = self.regular_user_client2.patch(ep, {'estado': MensajeDestinado.READED})
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.regular_user_client.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)

        # Tokened
        msg_user = MensajeDestinado.objects.filter(destinatario=self.user)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Self user OK
            resp = self.tokened_regular_client.patch(ep, {'estado': MensajeDestinado.READED})
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.tokened_regular_client2.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)

        msg_user = MensajeDestinado.objects.filter(destinatario=self.user2)
        for msg in msg_user:
            ep = f'/api/v1/mensajes/mensaje/{msg.id}/'
            # Self user OK
            resp = self.tokened_regular_client2.patch(ep, {'estado': MensajeDestinado.READED})
            if msg.estado == MensajeDestinado.DELETED:
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 200)
            # Other user 404
            resp = self.tokened_regular_client.patch(ep, {'estado': MensajeDestinado.READED})
            self.assertEqual(resp.status_code, 404)
