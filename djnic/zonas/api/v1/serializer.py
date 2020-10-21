from rest_framework import serializers
from zonas.models import Zona


class ZonaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Zona
        fields = ['id', 'nombre']