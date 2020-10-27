from django.urls import path, include
from rest_framework import routers
from .views_stats import GeneralStatsView, MayoresRegistrantesView


urlpatterns = [
    path('general', GeneralStatsView.as_view()),
    path('mayores-registrantes', MayoresRegistrantesView.as_view()),

]
