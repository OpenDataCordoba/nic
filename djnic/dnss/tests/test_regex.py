import logging
from django.test import TestCase
from dnss.models import Empresa, EmpresaRegexDomain, DNS

logger = logging.getLogger(__name__)
EMP1_REGEX1 = r'(.*).emp1.net$'
EMP1_REGEX2 = r'(.*).emp1.net.ar$'
EMP2_REGEX1 = r'(.*).pipo.emp2.ar$'
EMP2_REGEX2 = r'n1.(.*).emp2.br$'

class DNSRegexTestCase(TestCase):
    
    def test_regex_detection(self):
        
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=EMP1_REGEX1)
        logger.info(f'Regex defined {e1r1.regex_dns}')
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        dns2 = DNS.objects.create(dominio='ns2.emp2.net')
        dns3 = DNS.objects.create(dominio='ns1.emp1.net')

        self.assertEqual(dns1.empresa_regex, e1r1)
        self.assertEqual(dns3.empresa_regex, e1r1)
        self.assertIsNone(dns2.empresa_regex)

    def test_regex_manually_emp(self):
        
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=EMP1_REGEX1)
        logger.info(f'Regex defined {e1r1.regex_dns}')
        emp1.detect_DNSs()
        
        dns1 = DNS.objects.get(dominio='ns2.emp1.net')
        self.assertEqual(dns1.empresa_regex, e1r1)

    def test_regex_manually_regex(self):
        
        dns1 = DNS.objects.create(dominio='ns2.emp1.net')
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=EMP1_REGEX1)
        logger.info(f'Regex defined {e1r1.regex_dns}')
        e1r1.detect_DNSs()
        
        dns1 = DNS.objects.get(dominio='ns2.emp1.net')
        self.assertEqual(dns1.empresa_regex, e1r1)

    def test_regex_multiple(self):
        
        emp1 = Empresa.objects.create(nombre='Empresa 01')
        emp2 = Empresa.objects.create(nombre='Empresa 02')
        e1r1 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=EMP1_REGEX1)
        e1r2 = EmpresaRegexDomain.objects.create(empresa=emp1, regex_dns=EMP1_REGEX2)
        e2r1 = EmpresaRegexDomain.objects.create(empresa=emp2, regex_dns=EMP2_REGEX1)
        e2r2 = EmpresaRegexDomain.objects.create(empresa=emp2, regex_dns=EMP2_REGEX2)
        
        dns1 = DNS.objects.create(dominio='1.emp1.net')
        self.assertEqual(dns1.empresa_regex, e1r1)
        dns2 = DNS.objects.create(dominio='ns2.emp2.net')
        self.assertIsNone(dns2.empresa_regex)
        dns3 = DNS.objects.create(dominio='pipo.ns1.emp1.net')
        self.assertEqual(dns3.empresa_regex, e1r1)
        dns4 = DNS.objects.create(dominio='n1.emp1.net.ar')
        self.assertEqual(dns4.empresa_regex, e1r2)
        dns5 = DNS.objects.create(dominio='n1.emp1.net.br')
        self.assertIsNone(dns5.empresa_regex)
        dns6 = DNS.objects.create(dominio='.lalo.pipo.emp2.ar')
        self.assertEqual(dns6.empresa_regex, e2r1)
        dns7 = DNS.objects.create(dominio='pipo.emp2.ar')
        self.assertIsNone(dns7.empresa_regex)
        dns8 = DNS.objects.create(dominio='n1.pipo.emp2.br')
        self.assertEqual(dns8.empresa_regex, e2r2)
        dns9 = DNS.objects.create(dominio='n1.pipo.emp2.cl')
        self.assertIsNone(dns9.empresa_regex)
