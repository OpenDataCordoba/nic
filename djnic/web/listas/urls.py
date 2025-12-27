from django.urls import path
from web.listas.views import (
    DominiosUnaCaracterView,
    DominiosDosCaracteresView,
    CiudadesArgentinasView,
    PorteniosView,
    ProvinciasArgentinasListView,
)


urlpatterns = [
    path('provincias-argentinas', ProvinciasArgentinasListView.as_view(), name='listas-provincias-argentinas'),
    path('dominios-una-caracter', DominiosUnaCaracterView.as_view(), name='listas-dominios-una-caracter'),
    path('dominios-dos-caracteres', DominiosDosCaracteresView.as_view(), name='listas-dominios-dos-caracteres'),
    path('ciudades-argentinas', CiudadesArgentinasView.as_view(), name='listas-ciudades-argentinas'),
    path('portenios', PorteniosView.as_view(), name='listas-portenios'),
]
