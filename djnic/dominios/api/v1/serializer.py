from rest_framework import serializers
from dominios.models import Dominio


class DominioSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(read_only=True, source='full_domain')
    class Meta:
        model = Dominio
        
        fields = ['id', 'domain', 'data_updated', 'data_readed', 'estado',
                  'registered', 'changed', 'expire', 'priority_to_update',
                  'next_update_priority']    
                # TODO add zona
                # TODO add registrante
    