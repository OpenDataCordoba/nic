"""
Telegram bot webhook handler.

Handles incoming messages from Telegram:
- /start - Welcome message and registration info
- /link <token> - Link Telegram account to web user
- /unlink - Remove link to web account
- /status - Check current link status
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import requests
from channels.models import TelegramChannel, TelegramLinkToken, TelegramMessage
from channels.services.telegram import telegram_sender


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Handle incoming Telegram webhook updates.
    """

    def post(self, request):
        # Verify the secret token if configured
        webhook_secret = getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', None)
        if webhook_secret:
            provided_secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            if provided_secret != webhook_secret:
                logger.warning("Invalid Telegram webhook secret token")
                return HttpResponse('Forbidden', status=403)

        try:
            data = json.loads(request.body)
            self.process_update(data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Telegram webhook")
        except Exception as e:
            logger.exception(f"Error processing Telegram webhook: {e}")

        # Always return 200 to Telegram
        return HttpResponse('OK')

    def process_update(self, data):
        """Process a Telegram update."""
        message = data.get('message')
        if not message:
            return

        chat = message.get('chat', {})
        chat_id = chat.get('id')
        chat_type = chat.get('type')

        # Only handle private chats
        if chat_type != 'private':
            return

        text = message.get('text', '').strip()
        from_user = message.get('from', {})
        message_id = message.get('message_id')

        # Save incoming message
        self._save_incoming_message(chat_id, text, message_id, data)

        if text.startswith('/'):
            self.handle_command(chat_id, text, from_user)

    def _save_incoming_message(self, chat_id, text, message_id, raw_data):
        """Save an incoming message to the database."""
        try:
            channel = TelegramChannel.objects.filter(chat_id=chat_id).first()
            TelegramMessage.objects.create(
                channel=channel,
                chat_id=chat_id,
                direction=TelegramMessage.DIRECTION_IN,
                text=text,
                telegram_message_id=message_id,
                raw_data=raw_data
            )
        except Exception as e:
            logger.error(f"Error saving incoming message: {e}")

    def handle_command(self, chat_id, text, from_user):
        """Route commands to handlers."""
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''

        # Remove @botname if present
        if '@' in command:
            command = command.split('@')[0]

        handlers = {
            '/start': self.cmd_start,
            '/link': self.cmd_link,
            '/unlink': self.cmd_unlink,
            '/status': self.cmd_status,
            '/suscripciones': self.cmd_suscripciones,
            '/help': self.cmd_help,
        }

        handler = handlers.get(command, self.cmd_unknown)
        handler(chat_id, args, from_user)

    def cmd_start(self, chat_id, args, from_user):
        """Handle /start command."""
        # Check if user has a token to link
        if args:
            # /start with deep link token
            self.cmd_link(chat_id, args, from_user)
            return

        bot_name = settings.TELEGRAM_BOT_NAME
        site_name = settings.SITE_NAME

        # Check if already linked
        channel = TelegramChannel.objects.filter(chat_id=chat_id).first()

        if channel and channel.is_verified:
            message = (
                f"¡Hola <b>{self._escape(from_user.get('first_name', ''))}</b>\n\n"
                f"Tu cuenta de Telegram ya está vinculada a <b>{channel.user.username}</b> "
                f"en {site_name}.\n\n"
                f"Recibirás notificaciones aquí cuando haya cambios en tus suscripciones.\n\n"
                f"Comandos disponibles:\n"
                f"/suscripciones - Ver tus suscripciones\n"
                f"/status - Ver estado de tu cuenta\n"
                f"/unlink - Desvincular tu cuenta\n"
                f"/help - Ver ayuda"
            )
        else:
            message = (
                f"¡Bienvenido a <b>{bot_name}</b>!\n\n"
                f"Este bot te enviará notificaciones sobre cambios en dominios "
                f"y registrantes que sigas en {site_name}.\n\n"
                f"Para recibir notificaciones, vincula tu cuenta:\n\n"
                f"1. Ingresa a tu perfil en {site_name}\n"
                f"2. Ve a la sección de notificaciones\n"
                f"3. Haz clic en \"Vincular Telegram\"\n"
                f"4. Copia el código y envíalo aquí con:\n"
                f"   <code>/link TU_CODIGO</code>\n\n"
                f"Comandos disponibles:\n"
                f"/link &lt;código&gt; - Vincular tu cuenta\n"
                f"/status - Ver estado\n"
                f"/help - Ver ayuda"
            )

        telegram_sender.send_raw_message(chat_id, message)

    def cmd_link(self, chat_id, args, from_user):
        """Handle /link command - link Telegram to web account."""
        if not args:
            telegram_sender.send_raw_message(
                chat_id,
                "Debes proporcionar el código de vinculación.\n\n"
                "Uso: <code>/link TU_CODIGO</code>\n\n"
                "Obtén tu código desde tu perfil en la web."
            )
            return

        token_str = args.strip().upper()

        # Find valid token
        token = TelegramLinkToken.objects.filter(
            token=token_str,
            used=False
        ).first()

        if not token or not token.is_valid():
            telegram_sender.send_raw_message(
                chat_id,
                "Código inválido o expirado.\n\n"
                "Por favor, genera un nuevo código desde tu perfil en la web."
            )
            return

        # Check if this Telegram is already linked to another user
        existing = TelegramChannel.objects.filter(chat_id=chat_id).first()
        if existing and existing.user_id != token.user_id:
            telegram_sender.send_raw_message(
                chat_id,
                f"⚠️ Este Telegram ya está vinculado a otra cuenta "
                f"({existing.user.username}).\n\n"
                f"Usa /unlink primero si quieres vincular a otra cuenta."
            )
            return

        # Create or update TelegramChannel
        channel, created = TelegramChannel.objects.update_or_create(
            chat_id=chat_id,
            defaults={
                'user': token.user,
                'username': from_user.get('username', ''),
                'first_name': from_user.get('first_name', ''),
                'last_name': from_user.get('last_name', ''),
                'is_active': True,
                'is_verified': True,
            }
        )

        # Mark token as used
        token.used = True
        token.save(update_fields=['used'])

        telegram_sender.send_raw_message(
            chat_id,
            f"Cuenta vinculada exitosamente!\n\n"
            f"Tu Telegram ahora está conectado a <b>{token.user.username}</b>.\n\n"
            f"Recibirás notificaciones aquí cuando haya cambios "
            f"en tus suscripciones."
        )

        logger.info(f"Linked Telegram {chat_id} to user {token.user.username}")

    def cmd_unlink(self, chat_id, args, from_user):
        """Handle /unlink command."""
        channel = TelegramChannel.objects.filter(chat_id=chat_id).first()

        if not channel:
            telegram_sender.send_raw_message(
                chat_id,
                "Tu Telegram no está vinculado a ninguna cuenta."
            )
            return

        username = channel.user.username
        channel.delete()

        telegram_sender.send_raw_message(
            chat_id,
            f"Tu Telegram ha sido desvinculado de <b>{username}</b>.\n\n"
            f"Ya no recibirás notificaciones. "
            f"Usa /link para vincular nuevamente."
        )

        logger.info(f"Unlinked Telegram {chat_id} from user {username}")

    def cmd_status(self, chat_id, args, from_user):
        """Handle /status command."""
        channel = TelegramChannel.objects.filter(chat_id=chat_id).first()

        if not channel:
            telegram_sender.send_raw_message(
                chat_id,
                "ℹ<b>Estado:</b> No vinculado\n\n"
                "Tu Telegram no está vinculado a ninguna cuenta.\n"
                "Usa /link para vincular."
            )
            return

        status = "Activo" if channel.is_active else "Pausado"
        verified = "Verificado" if channel.is_verified else "Pendiente"

        last_sent = "Nunca"
        if channel.last_sent_at:
            last_sent = channel.last_sent_at.strftime("%d/%m/%Y %H:%M")

        message = (
            f"<b>Estado de tu cuenta</b>\n\n"
            f"Usuario: <b>{channel.user.username}</b>\n"
            f"Estado: {status}\n"
            f"Verificado: {verified}\n"
            f"Última notificación: {last_sent}\n"
        )

        if channel.error_count > 0:
            message += f"Errores recientes: {channel.error_count}\n"

        # Count subscriptions
        sub_count = channel.user.subscriptions.filter(is_active=True).count()
        message += f"\nSuscripciones activas: {sub_count}"

        telegram_sender.send_raw_message(chat_id, message)

    def cmd_suscripciones(self, chat_id, args, from_user):
        """Handle /suscripciones command - list user's active subscriptions."""
        channel = TelegramChannel.objects.filter(chat_id=chat_id).first()

        if not channel:
            telegram_sender.send_raw_message(
                chat_id,
                "Tu Telegram no está vinculado a ninguna cuenta.\n\n"
                "Usa /link para vincular primero."
            )
            return

        # Get active subscriptions
        from subscriptions.models import UserSubscription

        subscriptions = UserSubscription.objects.filter(
            user=channel.user,
            is_active=True
        ).select_related('target')

        if not subscriptions.exists():
            site_name = getattr(settings, 'SITE_NAME', 'NIC')
            telegram_sender.send_raw_message(
                chat_id,
                f"No tienes suscripciones activas.\n\n"
                f"Visita {site_name} para seguir dominios o registrantes."
            )
            return

        # Build message with subscriptions
        message_parts = ["<b>Tus suscripciones activas:</b>\n"]

        # Group by target type
        domain_subs = []
        registrant_subs = []

        for sub in subscriptions:
            target = sub.target
            if target.target_type == 'domain':
                domain_subs.append(sub)
            elif target.target_type == 'registrant':
                registrant_subs.append(sub)

        # Add domain subscriptions
        if domain_subs:
            message_parts.append("\n<b>Dominios:</b>")
            for sub in domain_subs:
                events = ", ".join(sub.event_types) if sub.event_types else "todos"
                delivery = sub.get_delivery_mode_display()
                message_parts.append(
                    f"• <b>{self._escape(sub.target.target_identifier)}</b>\n"
                    f"  Eventos: {events}\n"
                    f"  Entrega: {delivery}"
                )

        # Add registrant subscriptions
        if registrant_subs:
            message_parts.append("\n<b>Registrantes:</b>")
            for sub in registrant_subs:
                events = ", ".join(sub.event_types) if sub.event_types else "todos"
                delivery = sub.get_delivery_mode_display()
                message_parts.append(
                    f"• <b>{self._escape(sub.target.target_identifier)}</b>\n"
                    f"  Eventos: {events}\n"
                    f"  Entrega: {delivery}"
                )

        message_parts.append(f"\n<b>Total:</b> {subscriptions.count()} suscripciones")

        telegram_sender.send_raw_message(chat_id, "\n".join(message_parts))

    def cmd_help(self, chat_id, args, from_user):
        """Handle /help command."""
        site_name = getattr(settings, 'SITE_NAME', 'NIC')

        message = (
            "<b>Comandos disponibles</b>\n\n"
            "/start - Iniciar el bot\n"
            "/link &lt;código&gt; - Vincular tu cuenta\n"
            "/unlink - Desvincular tu cuenta\n"
            "/status - Ver estado de vinculación\n"
            "/suscripciones - Ver tus suscripciones activas\n"
            "/help - Ver esta ayuda\n\n"
            f"Para gestionar tus suscripciones, visita tu perfil en {site_name}."
        )

        telegram_sender.send_raw_message(chat_id, message)

    def cmd_unknown(self, chat_id, args, from_user):
        """Handle unknown commands."""
        telegram_sender.send_raw_message(
            chat_id,
            "Comando no reconocido.\n\n"
            "Usa /help para ver los comandos disponibles."
        )

    @staticmethod
    def _escape(text):
        """Escape HTML special characters."""
        if not text:
            return ''
        return (
            str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )


def setup_telegram_webhook(request):
    """
    View to set up the Telegram webhook.
    Should be called once during deployment.
    Access: Admin only.
    """

    # Require staff/admin user
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)

    bot_token = settings.TELEGRAM_BOT_TOKEN
    webhook_url = settings.TELEGRAM_WEBHOOK_URL
    webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET

    if not bot_token or not webhook_url:
        return JsonResponse({
            'error': 'TELEGRAM_BOT_TOKEN or TELEGRAM_WEBHOOK_URL not configured'
        }, status=400)

    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {'url': webhook_url}

    # Include secret token if configured
    if webhook_secret:
        payload['secret_token'] = webhook_secret

    response = requests.post(url, json=payload)
    data = response.json()

    if data.get('ok'):
        return JsonResponse({'success': True, 'message': 'Webhook set successfully'})
    else:
        return JsonResponse(
            {
                'error': data.get('description'),
                'webhook_url': webhook_url,
                'full_data_str': str(data),
            },
            status=400
        )
