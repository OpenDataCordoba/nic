from rest_framework import serializers
from dominios.models import Dominio


class DominioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dominio
        fields = ['id', 'nombre', 'data_updated', 'data_readed', 'estado',
                  'registered', 'changed', 'expire', 'priority_to_update',
                  'next_update_priority']    
                # TODO add zona
                # TODO add registrante
    