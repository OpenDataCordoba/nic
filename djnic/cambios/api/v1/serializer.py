from rest_framework import serializers
from cambios.models import CambiosDominio, CampoCambio


class CampoCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoCambio        
        fields = ['campo', 'anterior', 'nuevo']


class CambiosDominioSerializer(serializers.ModelSerializer):
    campos = CampoCambioSerializer(many=True)
    class Meta:
        model = CambiosDominio        
        fields = ['momento', 'campos']
