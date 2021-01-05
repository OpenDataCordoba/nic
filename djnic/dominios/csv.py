from core.csv import queryset_as_csv_view
from dominios.models import Dominio


def csv_dominios(request):
    """ CSV con los dominios en la base """

    fields = ['id', 'nombre', 'zona__nombre', 'estado', 'registered', 'changed', 'expire']
    override_fields = {
        'zona__nombre': 'zona'
    }
    queryset = Dominio.objects.values(*fields)
    response = queryset_as_csv_view(
        filename='dominios.csv',
        queryset=queryset,
        fields=fields,
        override_fields=override_fields)
    return response
