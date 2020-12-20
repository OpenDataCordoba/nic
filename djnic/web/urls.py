from django.urls import path, include
from .views import HomeView
from .views_dominio import (DominioView, UltimosCaidos,
                            UltimosRegistrados, Judicializados,
                            DominiosAntiguosView, DominiosVencimientoLargoView)
from .views_registrante import (RegistranteView, RubrosView,
                                RubroView, RegistrantesAntiguosView,
                                MayoresRegistrantesView)
from .views_dnss import HostingsView, Hostings30View, HostingView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dominio-<int:pk>', DominioView.as_view(), name='dominio'),
    path('registrante-<int:pk>', RegistranteView.as_view(), name='registrante'),

    # dominios
    path('ultimos-caidos', UltimosCaidos.as_view(), name='ultimos-caidos'),
    path('ultimos-registrados', UltimosRegistrados.as_view(), name='ultimos-registrados'),
    path('judicializados', Judicializados.as_view(), name='judicializados'),
    path('dominios-antiguos', DominiosAntiguosView.as_view(), name='dominios-antiguos'),
    path('dominios-futuros', DominiosVencimientoLargoView.as_view(), name='dominios-futuros'),

    # registrantes
    path('registrantes-antiguos', RegistrantesAntiguosView.as_view(), name='registrantes-antiguos'),
    path('rubros', RubrosView.as_view(), name='rubros'),
    path('rubro-<int:pk>', RubroView.as_view(), name='rubro'),
    path('mayores-registrantes', MayoresRegistrantesView.as_view(), name='mayores-registrantes'),

    # Hostings
    path('hostings', HostingsView.as_view(), name='hostings'),
    path('hostings-30', Hostings30View.as_view(), name='hostings-30'),
    path('hosting-<int:pk>', HostingView.as_view(), name='hosting'),

]
