from django.urls import path
from web.listas.views import (
    BebidasView,
    CiudadesArgentinasView,
    CiudadesMundoView,
    ComidasView,
    DominiosUnaCaracterView,
    DominiosDosCaracteresView,
    FinanzasView,
    FutbolistasView,
    PorteniosView,
    ProvinciasArgentinasListView,
)


urlpatterns = [
    path('provincias-argentinas', ProvinciasArgentinasListView.as_view(), name='listas-provincias-argentinas'),
    path('dominios-una-caracter', DominiosUnaCaracterView.as_view(), name='listas-dominios-una-caracter'),
    path('dominios-dos-caracteres', DominiosDosCaracteresView.as_view(), name='listas-dominios-dos-caracteres'),
    path('ciudades-argentinas', CiudadesArgentinasView.as_view(), name='listas-ciudades-argentinas'),
    path('ciudades-mundo', CiudadesMundoView.as_view(), name='listas-ciudades-mundo'),
    path('portenios', PorteniosView.as_view(), name='lista-portenios'),
    path('comidas', ComidasView.as_view(), name='lista-comidas'),
    path('bebidas', BebidasView.as_view(), name='lista-bebidas'),
    path('futbol', FutbolistasView.as_view(), name='lista-futbol'),
    path('finanzas', FinanzasView.as_view(), name='lista-finanzas'),
]
