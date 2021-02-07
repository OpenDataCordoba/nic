from rest_framework import serializers
from mensajes.models import MensajeDestinado, Mensaje


class MensajeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mensaje
        fields = ['id', 'titulo', 'texto']


class MensajeDestinadoSerializer(serializers.ModelSerializer):
    mensaje = MensajeSerializer(read_only=True)

    class Meta:
        model = MensajeDestinado
        fields = ['id', 'destinatario', 'estado', 'mensaje']
