from django.urls import path, include
from rest_framework import routers
from .views_stats import GeneralStatsView, PriorityView, ReadingStatsView


urlpatterns = [
    path('general', GeneralStatsView.as_view()),
    path('priority', PriorityView.as_view()),
    path('reading', ReadingStatsView.as_view()),
    path('reading/<str:desde_dias>', ReadingStatsView.as_view()),
    path('reading/<str:desde_dias>/<str:hasta_dias>', ReadingStatsView.as_view()),
    

]
