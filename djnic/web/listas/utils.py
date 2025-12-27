from dominios.models import Dominio
from zonas.models import Zona


def generate_lista_table(lista, zonas_relevantes=['com.ar', 'ar']):
    """ Generar un diccionario/tabla con todos los elementos de la lista como dominios
        para todas las zonas disponibles
    """

    # listar solo las zonas relevantes (quitar las que no se usan mucho)
    zonas = Zona.objects.filter(nombre__in=zonas_relevantes)
    res = {
        'dominios': {},
        'zonas': [zona.nombre for zona in zonas],
    }
    for dominio_str in lista:
        dominio_str = dominio_str.strip().lower()
        res['dominios'][dominio_str] = []
        for zona in zonas:
            dominio = Dominio.objects.filter(nombre=dominio_str, zona=zona).first()
            res['dominios'][dominio_str].append(dominio)

    return res
