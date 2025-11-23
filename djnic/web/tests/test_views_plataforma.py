from django.test import TestCase, Client
from django.urls import reverse

class StatsReadVtoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('stats-read-vto')

    def test_stats_read_vto_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/plataforma/stats-read-vto.html')

class StatsReadGeneralViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('stats-read-general')

    def test_stats_read_general_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/plataforma/stats-read-general.html')

class StatsRegistradosPorFechaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('registrados-por-fecha')

    def test_registrados_por_fecha_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/plataforma/registrados-por-fecha.html')

class StatsVencimientosPorFechaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('vencimientos-por-fecha')

    def test_vencimientos_por_fecha_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/bootstrap-base/plataforma/vencimientos-por-fecha.html')
