"""
Archivo hecho completamente por Sonnet 3.7
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class MensajeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('mensajes')
        # Create test user
        self.test_user = User.objects.create_user(username='testuser', password='12345')

    def test_mensaje_view_requires_login(self):
        # Test that view redirects when user is not logged in
        response = self.client.get(self.url)
        # 302 is redirect status code to login page
        self.assertEqual(response.status_code, 302)

    def test_mensaje_view_logged_in(self):
        # Log in the user
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/user/mensajes.html')
