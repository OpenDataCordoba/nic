from rest_framework import serializers
from registrantes.models import Registrante


class RegistrantSerializer(serializers.ModelSerializer):
    dominios_registrados = serializers.SerializerMethodField()

    def get_dominios_registrados(self, instance):
        from dominios.api.v1.serializer import MicroDominioSerializer
        return MicroDominioSerializer(instance.dominios, many=True).data

    class Meta:
        model = Registrante

        fields = ['id', 'name', 'zone', 'legal_uid', 'created', 'changed', 'dominios_registrados']
