"""
API views for channels app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from channels.models import TelegramChannel, TelegramLinkToken


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_telegram_link_token(request):
    """
    Generate a token for linking Telegram account.

    Returns a token that the user sends to the Telegram bot.
    """
    token = TelegramLinkToken.generate_token(request.user)

    return Response({
        'token': token.token,
        'expires_at': token.expires_at.isoformat(),
        'instructions': (
            f'Envía este código al bot de Telegram: /link {token.token}'
        )
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_telegram_status(request):
    """
    Get the user's Telegram channel status.
    """
    channel = TelegramChannel.objects.filter(user=request.user).first()

    if not channel:
        return Response({
            'linked': False,
            'message': 'No hay cuenta de Telegram vinculada'
        })

    return Response({
        'linked': True,
        'is_active': channel.is_active,
        'is_verified': channel.is_verified,
        'telegram_name': channel.get_display_name(),
        'last_sent_at': channel.last_sent_at.isoformat() if channel.last_sent_at else None,
        'error_count': channel.error_count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_telegram_channel(request):
    """
    Enable or disable Telegram notifications.
    """
    channel = TelegramChannel.objects.filter(user=request.user).first()

    if not channel:
        return Response({
            'error': 'No hay cuenta de Telegram vinculada'
        }, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action', 'toggle')

    if action == 'enable':
        channel.is_active = True
    elif action == 'disable':
        channel.is_active = False
    else:
        channel.is_active = not channel.is_active

    channel.save(update_fields=['is_active'])

    return Response({
        'is_active': channel.is_active,
        'message': 'Notificaciones activadas' if channel.is_active else 'Notificaciones desactivadas'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unlink_telegram(request):
    """
    Unlink Telegram account.
    """
    deleted_count, _ = TelegramChannel.objects.filter(user=request.user).delete()

    if deleted_count == 0:
        return Response({
            'error': 'No hay cuenta de Telegram vinculada'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'message': 'Cuenta de Telegram desvinculada'
    })
