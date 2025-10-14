from django.urls import path
from .views_stats import (GeneralStatsView, PriorityView, ReadingStatsView,
                          DominioPorFechaDeRegistroView,
                          DominioPorFechaDeVencimientoView)


urlpatterns = [
    path('general', GeneralStatsView.as_view()),
    path('priority', PriorityView.as_view()),
    path('reading', ReadingStatsView.as_view()),
    path('reading/<str:desde_dias>', ReadingStatsView.as_view()),
    path('reading/<str:desde_dias>/<str:hasta_dias>', ReadingStatsView.as_view()),
    path('registrados-por-fecha', DominioPorFechaDeRegistroView.as_view()),
    path('vencimientos-por-fecha', DominioPorFechaDeVencimientoView.as_view()),
]
