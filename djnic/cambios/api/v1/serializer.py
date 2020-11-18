from rest_framework import serializers
from cambios.models import CambiosDominio, CampoCambio


# serializadores cortos para poner dentro de los dominios
class CampoCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoCambio        
        fields = ['campo', 'anterior', 'nuevo']


class CambiosDominioSerializer(serializers.ModelSerializer):
    campos = CampoCambioSerializer(many=True)
    class Meta:
        model = CambiosDominio        
        fields = ['momento', 'campos']


class FullCampoCambioSerializer(serializers.ModelSerializer):
    full_domain = serializers.CharField(read_only=True, source='cambio.dominio.full_domain')
    domain_id = serializers.CharField(read_only=True, source='cambio.dominio.id')
    
    class Meta:
        model = CampoCambio        
        fields = ['full_domain', 'domain_id', 'campo', 'anterior', 'nuevo']


class FullCambiosDominioSerializer(serializers.ModelSerializer):
    full_domain = serializers.CharField(read_only=True, source='dominio.full_domain')
    domain_id = serializers.CharField(read_only=True, source='dominio.id')
    campos = CampoCambioSerializer(many=True)
    class Meta:
        model = CambiosDominio        
        fields = ['full_domain', 'domain_id', 'momento', 'have_changes', 'campos']
