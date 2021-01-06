from core.csv import queryset_as_csv_view
from dnss.models import Empresa, DNS


def csv_empresas(request):
    """ CSV con las empresas de hosting """

    fields = ['id', 'nombre']
    queryset = Empresa.objects.all()
    response = queryset_as_csv_view(request=request, filename='empresas.csv', queryset=queryset, fields=fields)
    return response


def csv_dns(request):
    """ CSV con los DNSs detectados """

    fields = ['id', 'dominio', 'empresa_regex__regex_dns', 'empresa_regex__empresa__nombre']
    override_fields = {
        'empresa_regex__regex_dns': 'Expresión regular',
        'empresa_regex__empresa__nombre': 'Empresa'
    }
    queryset = DNS.objects.values(*fields)
    response = queryset_as_csv_view(
        request=request,
        filename='dnss.csv',
        queryset=queryset,
        fields=fields,
        override_fields=override_fields)
    return response
