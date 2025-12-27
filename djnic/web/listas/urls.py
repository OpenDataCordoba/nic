from django.urls import path
from web.listas.views import ProvinciasArgentinasListView


urlpatterns = [
    path('provincias-argentinas', ProvinciasArgentinasListView.as_view(), name='listas-provincias-argentinas'),
]
