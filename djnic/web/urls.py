from django.urls import path, include
from .views import HomeView
from .views_dominio import DominioView, UltimosCaidos, UltimosRegistrados
from .views_registrante import RegistranteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dominio-<int:pk>', DominioView.as_view(), name='dominio'),
    path('registrante-<int:pk>', RegistranteView.as_view(), name='registrante'),
    path('ultimos-caidos', UltimosCaidos.as_view(), name='ultimos-caidos'),
    path('ultimos-registrados', UltimosRegistrados.as_view(), name='ultimos-registrados'),
]
