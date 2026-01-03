from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .views import (HomeView, AboutView, SearchResultsView,
                    PrivaciPolicyView, TermsView, LoginView)

from .views_dominio import (DominioView, UltimosCaidos,
                            UltimosRegistrados, Judicializados,
                            DominiosAntiguosView, DominiosVencimientoLargoView,
                            PorCaerView, SubscribeToDomainView,
                            UnsubscribeFromDomainView)
from .views_registrante import (RegistranteView, RubrosView,
                                RubroView, RegistrantesAntiguosView,
                                MayoresRegistrantesView, AddTagToRegistranteView,
                                CreateAndAddTagView, RemoveTagFromRegistranteView,
                                SubscribeToRegistranteView, UnsubscribeFromRegistranteView)
from .views_dnss import HostingsView, Hostings30View, HostingView, DNSView, PerdidasView
from .views_plataforma import (StatsReadVtoView, StatsReadGeneralView,
                               StatsRegistradosPorFechaView, StatsVencimientosPorFechaView)
from .views_cambios import RenovacionesView, RenovacionesRarasView, RenovacionesHaciaAtrasView
from .views_user import MensajeView

from dnss.csv import csv_empresas, csv_dns
from dominios.csv import csv_dominios


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dominio-<str:uid>', DominioView.as_view(), name='dominio'),
    path('about', AboutView.as_view(), name='about'),
    path('terminos-y-condiciones', TermsView.as_view(), name='terminos-y-condiciones'),
    path('politica-de-privacidad', PrivaciPolicyView.as_view(), name='politica-de-privacidad'),
    path('registrante-<str:uid>', RegistranteView.as_view(), name='registrante'),
    path('search/', SearchResultsView.as_view(), name='search'),

    # dominios
    path('ultimos-caidos', UltimosCaidos.as_view(), name='ultimos-caidos'),
    path('ultimos-registrados', UltimosRegistrados.as_view(), name='ultimos-registrados'),
    path('judicializados', Judicializados.as_view(), name='judicializados'),
    path('dominios-antiguos', DominiosAntiguosView.as_view(), name='dominios-antiguos'),
    path('dominios-futuros', DominiosVencimientoLargoView.as_view(), name='dominios-futuros'),
    path('renovaciones', RenovacionesView.as_view(), name='renovaciones'),
    path('renovaciones-raras', RenovacionesRarasView.as_view(), name='renovaciones-raras'),
    path('renovaciones-para-atras', RenovacionesHaciaAtrasView.as_view(), name='renovaciones-para-atras'),
    path('por-caer', PorCaerView.as_view(), name='por-caer'),

    # domain subscriptions (staff only)
    path('dominio-<str:uid>/subscribe', SubscribeToDomainView.as_view(), name='dominio-subscribe'),
    path('dominio-<str:uid>/unsubscribe', UnsubscribeFromDomainView.as_view(), name='dominio-unsubscribe'),

    # registrantes
    path('registrantes-antiguos', RegistrantesAntiguosView.as_view(), name='registrantes-antiguos'),
    path('rubros', RubrosView.as_view(), name='rubros'),
    path('rubro-<str:uid>', RubroView.as_view(), name='rubro'),
    path('mayores-registrantes', MayoresRegistrantesView.as_view(), name='mayores-registrantes'),

    # registrante tags (staff only)
    path('registrante-<str:uid>/add-tag', AddTagToRegistranteView.as_view(), name='registrante-add-tag'),
    path('registrante-<str:uid>/create-tag', CreateAndAddTagView.as_view(), name='registrante-create-tag'),
    path('registrante-<str:uid>/remove-tag', RemoveTagFromRegistranteView.as_view(), name='registrante-remove-tag'),

    # registrante subscriptions (staff only)
    path('registrante-<str:uid>/subscribe', SubscribeToRegistranteView.as_view(), name='registrante-subscribe'),
    path('registrante-<str:uid>/unsubscribe', UnsubscribeFromRegistranteView.as_view(), name='registrante-unsubscribe'),

    # Hostings
    path('hostings', HostingsView.as_view(), name='hostings'),
    path('hostings-30', Hostings30View.as_view(), name='hostings-30'),
    path('hosting-<str:uid>', HostingView.as_view(), name='hosting'),
    path('dns-<str:uid>', DNSView.as_view(), name='dns'),
    path('hostings-perdidas-30', PerdidasView.as_view(), name='hostings-perdidas-30'),

    # Estadísticas de la plataforma
    path('stats-read-general', StatsReadGeneralView.as_view(), name='stats-read-general'),
    path('stats-read-vto', StatsReadVtoView.as_view(), name='stats-read-vto'),
    path('registrados-por-fecha', StatsRegistradosPorFechaView.as_view(), name='registrados-por-fecha'),
    path('vencimientos-por-fecha', StatsVencimientosPorFechaView.as_view(), name='vencimientos-por-fecha'),

    # Usuarios
    path('login/', LoginView.as_view(), name='clogin'),
    path('mensajes/', login_required(MensajeView.as_view()), name='mensajes'),

    # descargas CSV
    path('descargas/empresas.csv', csv_empresas, name='csv-empresas'),
    path('descargas/dnss.csv', csv_dns, name='csv-dnss'),
    path('descargas/dominios.csv', csv_dominios, name='csv-dominios'),

    # Listas predefinidas
    # listas/* sent to listas/urls.py
    path('listas/', include('web.listas.urls'))
]
