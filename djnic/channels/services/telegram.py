"""
Telegram notification sender service.
"""
import logging
from typing import Dict, Any
from django.conf import settings

from subscriptions.models import UserNotification
from channels.models import TelegramChannel, TelegramMessage, NotificationChannel
from channels.services import NotificationSender, NotificationRegistry


logger = logging.getLogger(__name__)


class TelegramSender(NotificationSender):
    """
    Sends notifications via Telegram Bot API.
    """

    channel_type = NotificationChannel.CHANNEL_TYPE_TELEGRAM

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_base = 'https://api.telegram.org/bot'

    def get_active_channels(self, user):
        """Get all active Telegram channels for a user."""
        return TelegramChannel.objects.filter(
            user=user,
            is_active=True,
            is_verified=True
        )

    def format_message(self, notification: UserNotification) -> str:
        """
        Format notification for Telegram (HTML format).
        """
        event_data = notification.event_data or {}

        # Build message parts
        parts = []

        # Title/header
        if notification.title:
            parts.append(f"<b>{self._escape_html(notification.title)}</b>")

        # Description from event_data
        description = event_data.get('description', '')
        if description:
            parts.append(f"\n{self._escape_html(description)}")

        # Domain info
        domain = event_data.get('domain', '')
        if domain:
            domain_url = event_data.get('domain_url', '')
            if domain_url:
                # Make domain clickable
                full_url = self._build_full_url(domain_url)
                parts.append(f"\n<a href=\"{full_url}\">{self._escape_html(domain)}</a>")

        # Add relevant dates/changes
        anterior = event_data.get('anterior', '')
        nuevo = event_data.get('nuevo', '')
        if anterior or nuevo:
            if anterior and nuevo:
                parts.append(f"\n{self._escape_html(anterior)} → {self._escape_html(nuevo)}")

        # Footer with timestamp
        if notification.event_date:
            parts.append(f"\n\n{notification.event_date.strftime('%d/%m/%Y')}")

        return ''.join(parts)

    def send(self, channel: TelegramChannel, notification: UserNotification) -> Dict[str, Any]:
        """
        Send notification to a Telegram channel.
        """
        if not self.bot_token:
            return {
                'success': False,
                'error': 'TELEGRAM_BOT_TOKEN not configured'
            }

        import requests

        message = self.format_message(notification)
        url = f"{self.api_base}{self.bot_token}/sendMessage"

        payload = {
            'chat_id': channel.chat_id,
            'text': message,
            'parse_mode': channel.parse_mode,
            'disable_web_page_preview': channel.disable_preview,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()

            if data.get('ok'):
                message_id = data.get('result', {}).get('message_id', '')
                logger.info(
                    f"Sent Telegram notification to chat {channel.chat_id}, "
                    f"message_id: {message_id}"
                )
                self._save_outgoing_message(channel.chat_id, message, message_id, channel)
                return {
                    'success': True,
                    'external_id': str(message_id)
                }
            else:
                error_desc = data.get('description', 'Unknown Telegram API error')
                error_code = data.get('error_code', '')

                # Handle specific errors
                if error_code == 403:
                    # User blocked the bot - deactivate channel
                    channel.is_active = False
                    channel.save(update_fields=['is_active'])
                    logger.warning(
                        f"User blocked bot, deactivating channel {channel.id}"
                    )

                return {
                    'success': False,
                    'error': f"Telegram API error {error_code}: {error_desc}"
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Telegram API timeout'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }

    def send_raw_message(self, chat_id: int, text: str, parse_mode: str = 'HTML') -> Dict[str, Any]:
        """
        Send a raw message to a chat (for bot commands, not notifications).
        """
        if not self.bot_token:
            return {'success': False, 'error': 'TELEGRAM_BOT_TOKEN not configured'}

        import requests

        url = f"{self.api_base}{self.bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()

            if data.get('ok'):
                message_id = data['result']['message_id']
                self._save_outgoing_message(chat_id, text, message_id)
                return {'success': True, 'message_id': message_id}
            else:
                return {'success': False, 'error': data.get('description', 'Unknown error')}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ''
        return (
            str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )

    @staticmethod
    def _build_full_url(path: str) -> str:
        """Build full URL from a path."""
        base_url = getattr(settings, 'SITE_BASE_URL', 'https://example.com')
        if path.startswith('http'):
            return path
        return f"{base_url.rstrip('/')}{path}"

    def _save_outgoing_message(self, chat_id: int, text: str, message_id: int, channel: TelegramChannel = None):
        """Save an outgoing message to the database."""
        try:
            if channel is None:
                channel = TelegramChannel.objects.filter(chat_id=chat_id).first()
            TelegramMessage.objects.create(
                channel=channel,
                chat_id=chat_id,
                direction=TelegramMessage.DIRECTION_OUT,
                text=text,
                telegram_message_id=message_id
            )
        except Exception as e:
            logger.error(f"Error saving outgoing message: {e}")


# Register the Telegram sender
telegram_sender = TelegramSender()
NotificationRegistry.register(telegram_sender)
