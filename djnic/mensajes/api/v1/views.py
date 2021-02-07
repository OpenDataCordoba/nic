import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from mensajes.models import MensajeDestinado
from mensajes.data import get_messages
from .serializer import MensajeDestinadoSerializer


logger = logging.getLogger(__name__)


class MessageOwnerPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in list(SAFE_METHODS) + ['PATCH', 'DELETE']:
            return obj.destinatario == request.user
        return False

    def has_permission(self, request, view):
        return True


class MensajeDestinadoViewSet(viewsets.ModelViewSet):

    serializer_class = MensajeDestinadoSerializer
    permission_classes = [MessageOwnerPermission]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    ordering = ['-created']

    def get_queryset(self):
        return get_messages(user=self.request.user)

    def partial_update(self, request, pk=None):
        # only allow "estado" to be updated
        new_estado = int(request.data['estado'])
        valid_estados = [MensajeDestinado.CREATED, MensajeDestinado.READED, MensajeDestinado.DELETED]
        if new_estado not in valid_estados:
            return Response({'error': f'{new_estado} is not a valid estado ({valid_estados})'}, status=status.HTTP_400_BAD_REQUEST)
        msg = self.get_object()
        msg.estado = new_estado
        msg.save()
        logger.error(f'Message readed {msg}')

        return Response({'status': 'Updated'}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        msg = self.get_object()
        msg.estado = MensajeDestinado.DELETED
        msg.save()
        logger.error(f'Message deleted {msg}')

        return Response({'status': 'Deleted'}, status=status.HTTP_200_OK)
