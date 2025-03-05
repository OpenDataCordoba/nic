"""
Archivo hecho completamente por Sonnet 3.7
"""
from django.test import TestCase, Client
from django.urls import reverse


class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('home')

    def test_home_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/home.html')


class TermsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('terminos-y-condiciones')

    def test_terms_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/terms_of_service.html')


class PrivacyPolicyViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('politica-de-privacidad')

    def test_privacy_policy_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/privacy_policy.html')


class AboutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('about')

    def test_about_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/about.html')


class SearchResultsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('search')

    def test_search_results_view(self):
        response = self.client.get(self.url, {'query': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/search.html')


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('clogin')

    def test_login_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/login.html')
