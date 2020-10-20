from django.urls import path, include
from rest_framework import routers
from .views import DominioViewSet


router = routers.DefaultRouter()
router.register(r'dominio', DominioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
