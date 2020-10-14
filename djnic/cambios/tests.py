from datetime import datetime 
from django.test import TestCase
from dominios.models import Dominio
from cambios.models import CambiosDominio, CampoCambio

from whoare.exceptions import (TooManyQueriesError, ServiceUnavailableError, 
                               UnknownError, UnexpectedParseError,
                               UnexpectedDomainError, ZoneNotFoundError)

class CambioDominioTestCase(TestCase):
    
    def test_change_new_domain(self):

        with self.assertRaises(ZoneNotFoundError):
            Dominio.add_from_whois('some.fake.ar', mock_from_txt_file='djnic/whosamples/sample_fernet.txt')
        
        with self.assertRaises(UnexpectedDomainError):
            Dominio.add_from_whois('fake.com.ar', mock_from_txt_file='djnic/whosamples/sample_fernet.txt')
        
        dominio = Dominio.add_from_whois('fernet.com.ar', mock_from_txt_file='djnic/whosamples/sample_fernet.txt')
        # nothing change until here
        self.assertEqual(dominio.cambios.count(), 0)
        self.assertEqual(dominio.dnss.count(), 2)
        
        dominio2 = Dominio.add_from_whois('fernet.com.ar', mock_from_txt_file='djnic/whosamples/sample_fernet_updated.txt')
        self.assertEqual(dominio.cambios.count(), 1)
        self.assertEqual(dominio.cambios.first().campos.count(), 8)
        
        main_change = CambiosDominio.objects.all()[0]
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='dominio_registered', anterior='2020-05-07 10:44:04', nuevo='2021-05-07 10:44:04').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='dominio_changed', anterior='2020-05-07 14:34:40', nuevo='2021-05-07 14:34:40').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='dominio_expire', anterior='2021-05-07 00:00:00', nuevo='2022-05-07 00:00:00').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='registrant_name', anterior='perez juan', nuevo='gonzalez pedro').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='registrant_legal_uid', anterior='20xxxxxxxx9', nuevo='20xxxxxxxx8').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='registrant_created', anterior='2013-08-19 00:00:00', nuevo='2020-08-19 00:00:00').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='DNS1', anterior='ns2.sedoparking.com', nuevo='ns30.polonia.com').count(), 1)
        self.assertEqual(CampoCambio.objects.filter(cambio=main_change, campo='DNS2', anterior='ns1.sedoparking.com', nuevo='ns40.polonia.com').count(), 1)

        
        
        