from core.csv import queryset_as_csv_view
from dominios.models import Dominio, STATUS_NO_DISPONIBLE


def csv_dominios(request):
    """ CSV con los dominios en la base """

    fields = ['id', 'nombre', 'zona__nombre', 'estado', 'registered', 'changed', 'expire']
    override_fields = {
        'zona__nombre': 'zona'
    }
    queryset = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE).values(*fields)
    response = queryset_as_csv_view(
        request=request,
        filename='dominios.csv',
        queryset=queryset,
        fields=fields,
        override_fields=override_fields)
    return response
