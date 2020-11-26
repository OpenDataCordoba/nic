from django.test import TestCase
from dnss.models import Empresa, EmpresaRegexDomain, DNS


class DNSRegexTestCase(TestCase):
    
    def test_regex_detection(self):
        
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=r'(.*)[.]emp1[.]net$')
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        dns2 = DNS.objects.create(dominio='ns2.emp2.net')
        dns3 = DNS.objects.create(dominio='ns1.emp1.net')

        self.assertEqual(dns1.empresa_regex, e1r1)
        self.assertEqual(dns3.empresa_regex, e1r1)
        self.assertIsNone(dns2.empresa_regex)

    def test_regex_manually_emp(self):
        
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=r'(.*)[.]emp1[.]net$')
        emp1.detect_DNSs()
        
        self.assertEqual(dns1.empresa_regex, e1r1)

    def test_regex_manually_regex(self):
        
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=r'(.*)[.]emp1[.]net$')
        e1r1.detect_DNSs()
        
        self.assertEqual(dns1.empresa_regex, e1r1)