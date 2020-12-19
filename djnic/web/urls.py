from django.urls import path, include
from .views import HomeView
from .views_dominio import DominioView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dominio-<int:pk>', DominioView.as_view(), name='dominio'),
]
