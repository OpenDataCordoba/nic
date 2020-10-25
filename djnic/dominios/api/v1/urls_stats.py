from django.urls import path, include
from rest_framework import routers
from .views_stats import GeneralStatsView, PriorityView


urlpatterns = [
    path('general', GeneralStatsView.as_view()),
    path('priority', PriorityView.as_view()),

]
