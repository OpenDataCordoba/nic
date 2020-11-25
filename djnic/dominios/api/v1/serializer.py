from rest_framework import serializers
from dominios.models import Dominio, PreDominio
from registrantes.api.v1.serializer import RegistrantSerializer
from cambios.api.v1.serializer import CambiosDominioSerializer


class DominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='full_domain')
    registrante = RegistrantSerializer(required=False)
    cambios = CambiosDominioSerializer(many=True, required=False)

    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'data_updated', 'data_readed', 'estado',
                  'registered', 'changed', 'expire', 'priority_to_update',
                  'next_update_priority', 'registrante', 'cambios']


class FlatDominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='full_domain')
    
    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'data_updated', 'data_readed', 'estado',
                  'registered', 'changed', 'expire', 'priority_to_update',
                  'next_update_priority']

class FlatPreDominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='dominio')
    
    class Meta:
        model = PreDominio
        fields = ['id', 'domain']


class PreDominioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PreDominio
        fields = ['id', 'dominio', 'priority']

class CambiosDominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='full_domain')
    ultimo_cambio = CambiosDominioSerializer()

    class Meta:
        model = Dominio
        fields = ['id', 'domain', 'data_updated', 'ultimo_cambio']


class MicroDominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='full_domain')
    
    class Meta:
        model = Dominio
        fields = ['id', 'domain']

