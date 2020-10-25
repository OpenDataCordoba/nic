from rest_framework import serializers
from registrantes.models import Registrante


class RegistrantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Registrante
        
        fields = ['id', 'name', 'zone', 'legal_uid', 'created', 'changed']    
  