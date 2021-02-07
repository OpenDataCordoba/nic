from django.urls import path, include
from rest_framework import routers
from .views import MensajeDestinadoViewSet


router = routers.DefaultRouter()
router.register(r'mensaje', MensajeDestinadoViewSet, basename='mensaje')

urlpatterns = [
    path('', include(router.urls)),
]
