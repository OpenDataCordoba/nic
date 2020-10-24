from django.urls import path, include
from rest_framework import routers
from .views_stats import GeneralStatsViews


urlpatterns = [
    path('general', GeneralStatsViews.as_view()),
    
]
