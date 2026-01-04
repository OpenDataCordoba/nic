"""
Tests for the channels app.
"""
import json
from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.utils import timezone

from channels.models import (
    TelegramChannel, TelegramLinkToken, NotificationChannel,
    TelegramMessage
)
from channels.services.telegram import TelegramSender
from subscriptions.models import UserNotification


class TelegramChannelModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_telegram_channel(self):
        channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            username='testuser_tg',
            first_name='Test',
            last_name='User',
        )

        self.assertEqual(channel.channel_type, NotificationChannel.CHANNEL_TYPE_TELEGRAM)
        self.assertTrue(channel.is_active)
        self.assertFalse(channel.is_verified)

    def test_get_display_name_with_username(self):
        channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            username='testuser_tg',
        )
        self.assertEqual(channel.get_display_name(), '@testuser_tg')

    def test_get_display_name_with_name(self):
        channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            first_name='Test',
            last_name='User',
        )
        self.assertEqual(channel.get_display_name(), 'Test User')

    def test_get_display_name_fallback(self):
        channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
        )
        self.assertEqual(channel.get_display_name(), 'Chat 123456789')


class TelegramLinkTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_generate_token(self):
        token = TelegramLinkToken.generate_token(self.user)

        self.assertIsNotNone(token.token)
        self.assertEqual(len(token.token), 16)
        self.assertFalse(token.used)
        self.assertTrue(token.is_valid())

    def test_token_expiry(self):
        token = TelegramLinkToken.generate_token(self.user, expiry_minutes=0)
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()

        self.assertFalse(token.is_valid())

    def test_invalidate_old_tokens(self):
        token1 = TelegramLinkToken.generate_token(self.user)
        token2 = TelegramLinkToken.generate_token(self.user)

        token1.refresh_from_db()
        self.assertTrue(token1.used)  # Old token invalidated
        self.assertFalse(token2.used)  # New token active


class TelegramSenderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )
        self.sender = TelegramSender()

    def test_format_message(self):
        notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            event_data={
                'description': 'Domain example.com was dropped',
                'domain': 'example.com',
                'domain_url': '/dominio/123/',
            },
            event_date=timezone.now().date(),
        )

        message = self.sender.format_message(notification)

        self.assertIn('Test Notification', message)
        self.assertIn('example.com', message)
        self.assertIn('dropped', message)

    @patch('channels.services.telegram.requests.post')
    @override_settings(TELEGRAM_BOT_TOKEN='test-token')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ok': True,
            'result': {'message_id': 12345}
        }
        mock_post.return_value = mock_response

        notification = UserNotification.objects.create(
            user=self.user,
            title='Test',
            event_data={'description': 'Test message'},
        )

        result = self.sender.send(self.channel, notification)

        self.assertTrue(result['success'])
        self.assertEqual(result['external_id'], '12345')

    @patch('channels.services.telegram.requests.post')
    @override_settings(TELEGRAM_BOT_TOKEN='test-token')
    def test_send_blocked_user(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ok': False,
            'error_code': 403,
            'description': 'Forbidden: bot was blocked by the user'
        }
        mock_post.return_value = mock_response

        notification = UserNotification.objects.create(
            user=self.user,
            title='Test',
            event_data={},
        )

        result = self.sender.send(self.channel, notification)

        self.assertFalse(result['success'])

        # Channel should be deactivated
        self.channel.refresh_from_db()
        self.assertFalse(self.channel.is_active)


class TelegramWebhookTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_start_command(self, mock_send):
        mock_send.return_value = {'success': True}

        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'from': {'id': 123456789, 'first_name': 'Test'},
                    'text': '/start'
                }
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_command_success(self, mock_send):
        mock_send.return_value = {'success': True}

        # Generate a token
        token = TelegramLinkToken.generate_token(self.user)

        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'from': {
                        'id': 123456789,
                        'first_name': 'Test',
                        'username': 'testuser_tg'
                    },
                    'text': f'/link {token.token}'
                }
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Channel should be created
        channel = TelegramChannel.objects.filter(chat_id=123456789).first()
        self.assertIsNotNone(channel)
        self.assertEqual(channel.user, self.user)
        self.assertTrue(channel.is_verified)

        # Token should be used
        token.refresh_from_db()
        self.assertTrue(token.used)


class ChannelAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_generate_link_token(self):
        response = self.client.post('/channels/api/telegram/link-token/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)
        self.assertIn('expires_at', data)

    def test_get_telegram_status_not_linked(self):
        response = self.client.get('/channels/api/telegram/status/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['linked'])

    def test_get_telegram_status_linked(self):
        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
            username='testuser_tg',
        )

        response = self.client.get('/channels/api/telegram/status/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['linked'])
        self.assertTrue(data['is_active'])
        self.assertEqual(data['telegram_name'], '@testuser_tg')

    def test_toggle_telegram_channel(self):
        channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        response = self.client.post(
            '/channels/api/telegram/toggle/',
            data=json.dumps({'action': 'disable'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        channel.refresh_from_db()
        self.assertFalse(channel.is_active)

    def test_unlink_telegram(self):
        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
        )

        response = self.client.delete('/channels/api/telegram/unlink/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            TelegramChannel.objects.filter(user=self.user).exists()
        )


class TelegramMessageModelTest(TestCase):
    """Tests for TelegramMessage model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

    def test_create_incoming_message(self):
        message = TelegramMessage.objects.create(
            channel=self.channel,
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_IN,
            text='/start',
            telegram_message_id=100,
            raw_data={'message': {'text': '/start'}}
        )

        self.assertEqual(message.direction, 'in')
        self.assertEqual(message.text, '/start')
        self.assertIsNotNone(message.raw_data)

    def test_create_outgoing_message(self):
        message = TelegramMessage.objects.create(
            channel=self.channel,
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_OUT,
            text='Welcome!',
            telegram_message_id=101,
        )

        self.assertEqual(message.direction, 'out')
        self.assertIsNone(message.raw_data)

    def test_message_without_channel(self):
        """Messages can be created without a linked channel."""
        message = TelegramMessage.objects.create(
            channel=None,
            chat_id=999999999,
            direction=TelegramMessage.DIRECTION_IN,
            text='/start',
        )

        self.assertIsNone(message.channel)
        self.assertEqual(message.chat_id, 999999999)

    def test_str_representation(self):
        message_in = TelegramMessage.objects.create(
            channel=self.channel,
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_IN,
            text='Hello bot',
        )
        message_out = TelegramMessage.objects.create(
            channel=self.channel,
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_OUT,
            text='Hello user',
        )

        self.assertIn('←', str(message_in))
        self.assertIn('→', str(message_out))

    def test_long_text_truncated_in_str(self):
        long_text = 'A' * 100
        message = TelegramMessage.objects.create(
            channel=self.channel,
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_IN,
            text=long_text,
        )

        self.assertIn('...', str(message))
        self.assertLess(len(str(message)), len(long_text) + 20)


class WebhookSecurityTest(TestCase):
    """Tests for webhook security features."""

    def setUp(self):
        self.client = Client()

    @override_settings(TELEGRAM_WEBHOOK_SECRET='test-secret-123')
    def test_webhook_rejects_missing_secret(self):
        """Webhook should reject requests without secret header."""
        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'text': '/start'
                }
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(TELEGRAM_WEBHOOK_SECRET='test-secret-123')
    def test_webhook_rejects_wrong_secret(self):
        """Webhook should reject requests with wrong secret."""
        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'text': '/start'
                }
            }),
            content_type='application/json',
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN='wrong-secret'
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(TELEGRAM_WEBHOOK_SECRET='test-secret-123')
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_webhook_accepts_correct_secret(self, mock_send):
        """Webhook should accept requests with correct secret."""
        mock_send.return_value = {'success': True}

        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'from': {'id': 123456789, 'first_name': 'Test'},
                    'text': '/start'
                }
            }),
            content_type='application/json',
            HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN='test-secret-123'
        )

        self.assertEqual(response.status_code, 200)

    @override_settings(TELEGRAM_WEBHOOK_SECRET=None)
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_webhook_allows_no_secret_when_not_configured(self, mock_send):
        """Webhook should work without secret when not configured."""
        mock_send.return_value = {'success': True}

        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'chat': {'id': 123456789, 'type': 'private'},
                    'from': {'id': 123456789, 'first_name': 'Test'},
                    'text': '/start'
                }
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)


class SetupWebhookSecurityTest(TestCase):
    """Tests for setup_telegram_webhook endpoint security."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123',
            is_staff=False
        )

    def test_setup_webhook_rejects_anonymous(self):
        """Setup webhook should reject anonymous users."""
        response = self.client.get('/channels/telegram/setup-webhook/')

        self.assertEqual(response.status_code, 403)

    def test_setup_webhook_rejects_non_staff(self):
        """Setup webhook should reject non-staff users."""
        self.client.login(username='normaluser', password='normalpass123')

        response = self.client.get('/channels/telegram/setup-webhook/')

        self.assertEqual(response.status_code, 403)

    @override_settings(TELEGRAM_BOT_TOKEN=None)
    def test_setup_webhook_requires_token_config(self):
        """Setup webhook should require TELEGRAM_BOT_TOKEN."""
        self.client.login(username='admin', password='adminpass123')

        response = self.client.get('/channels/telegram/setup-webhook/')

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    @patch('channels.views.requests.post')
    @override_settings(
        TELEGRAM_BOT_TOKEN='test-token',
        TELEGRAM_WEBHOOK_URL='https://example.com/webhook/',
        TELEGRAM_WEBHOOK_SECRET='test-secret'
    )
    def test_setup_webhook_success(self, mock_post):
        """Setup webhook should succeed for admin with config."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'ok': True}
        mock_post.return_value = mock_response

        self.client.login(username='admin', password='adminpass123')

        response = self.client.get('/channels/telegram/setup-webhook/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify secret was included in payload
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['secret_token'], 'test-secret')


class MessageLoggingTest(TestCase):
    """Tests for message logging functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.channel = TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )
        self.sender = TelegramSender()

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_incoming_message_logged(self, mock_send):
        """Incoming messages should be saved to database."""
        mock_send.return_value = {'success': True, 'message_id': 200}

        self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'message_id': 100,
                    'chat': {'id': 123456789, 'type': 'private'},
                    'from': {'id': 123456789, 'first_name': 'Test'},
                    'text': '/status'
                }
            }),
            content_type='application/json'
        )

        # Check incoming message was saved
        incoming = TelegramMessage.objects.filter(
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_IN
        ).first()

        self.assertIsNotNone(incoming)
        self.assertEqual(incoming.text, '/status')
        self.assertEqual(incoming.telegram_message_id, 100)
        self.assertIsNotNone(incoming.raw_data)
        self.assertEqual(incoming.channel, self.channel)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_incoming_message_logged_without_channel(self, mock_send):
        """Incoming messages from unlinked users should also be saved."""
        mock_send.return_value = {'success': True, 'message_id': 200}

        self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'message_id': 100,
                    'chat': {'id': 999999999, 'type': 'private'},
                    'from': {'id': 999999999, 'first_name': 'Unknown'},
                    'text': '/start'
                }
            }),
            content_type='application/json'
        )

        incoming = TelegramMessage.objects.filter(
            chat_id=999999999,
            direction=TelegramMessage.DIRECTION_IN
        ).first()

        self.assertIsNotNone(incoming)
        self.assertIsNone(incoming.channel)  # No channel for unlinked user

    @patch('channels.services.telegram.requests.post')
    @override_settings(TELEGRAM_BOT_TOKEN='test-token')
    def test_outgoing_notification_logged(self, mock_post):
        """Outgoing notifications should be saved to database."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ok': True,
            'result': {'message_id': 12345}
        }
        mock_post.return_value = mock_response

        notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            event_data={'description': 'Test'},
        )

        self.sender.send(self.channel, notification)

        outgoing = TelegramMessage.objects.filter(
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_OUT
        ).first()

        self.assertIsNotNone(outgoing)
        self.assertEqual(outgoing.telegram_message_id, 12345)
        self.assertEqual(outgoing.channel, self.channel)
        self.assertIn('Test Notification', outgoing.text)

    @patch('channels.services.telegram.requests.post')
    @override_settings(TELEGRAM_BOT_TOKEN='test-token')
    def test_outgoing_raw_message_logged(self, mock_post):
        """Outgoing raw messages should be saved to database."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ok': True,
            'result': {'message_id': 54321}
        }
        mock_post.return_value = mock_response

        self.sender.send_raw_message(123456789, 'Hello from bot!')

        outgoing = TelegramMessage.objects.filter(
            chat_id=123456789,
            direction=TelegramMessage.DIRECTION_OUT,
            text='Hello from bot!'
        ).first()

        self.assertIsNotNone(outgoing)
        self.assertEqual(outgoing.telegram_message_id, 54321)

    @patch('channels.services.telegram.requests.post')
    @override_settings(TELEGRAM_BOT_TOKEN='test-token')
    def test_failed_send_not_logged(self, mock_post):
        """Failed sends should not create message records."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ok': False,
            'error_code': 400,
            'description': 'Bad Request'
        }
        mock_post.return_value = mock_response

        initial_count = TelegramMessage.objects.count()

        self.sender.send_raw_message(123456789, 'This will fail')

        # No new message should be created
        self.assertEqual(TelegramMessage.objects.count(), initial_count)


class TelegramBotCommandsTest(TestCase):
    """Comprehensive tests for Telegram bot commands."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def _send_command(self, chat_id, text, first_name='Test', username=None):
        """Helper to send a command to the webhook."""
        from_user = {'id': chat_id, 'first_name': first_name}
        if username:
            from_user['username'] = username

        return self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'message_id': 100,
                    'chat': {'id': chat_id, 'type': 'private'},
                    'from': from_user,
                    'text': text
                }
            }),
            content_type='application/json'
        )

    # /start command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_start_command_unlinked_user(self, mock_send):
        """Test /start for user without linked account."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/start')

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

        # Check message contains welcome info
        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Bienvenido', message)
        self.assertIn('/link', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_start_command_linked_user(self, mock_send):
        """Test /start for user with linked account."""
        mock_send.return_value = {'success': True}

        # Create linked channel
        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        response = self._send_command(123456789, '/start', first_name='Juan')

        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

        # Check message confirms linked status
        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Hola', message)
        self.assertIn('testuser', message)
        self.assertIn('vinculada', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_start_with_deep_link_token(self, mock_send):
        """Test /start with deep link token (same as /link)."""
        mock_send.return_value = {'success': True}

        token = TelegramLinkToken.generate_token(self.user)

        response = self._send_command(123456789, f'/start {token.token}', username='tg_user')

        self.assertEqual(response.status_code, 200)

        # Channel should be created
        channel = TelegramChannel.objects.filter(chat_id=123456789).first()
        self.assertIsNotNone(channel)
        self.assertTrue(channel.is_verified)

    # /link command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_without_token(self, mock_send):
        """Test /link without providing a token."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/link')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('proporcionar', message)
        self.assertIn('TU_CODIGO', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_with_invalid_token(self, mock_send):
        """Test /link with invalid token."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/link INVALIDTOKEN123')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('inválido', message.lower())

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_with_expired_token(self, mock_send):
        """Test /link with expired token."""
        mock_send.return_value = {'success': True}

        # Create expired token
        token = TelegramLinkToken.generate_token(self.user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()

        response = self._send_command(123456789, f'/link {token.token}')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('expirado', message.lower())

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_already_linked_to_another_user(self, mock_send):
        """Test /link when chat is already linked to another user."""
        mock_send.return_value = {'success': True}

        # Create existing channel for another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        TelegramChannel.objects.create(
            user=other_user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        # Try to link to our user
        token = TelegramLinkToken.generate_token(self.user)

        response = self._send_command(123456789, f'/link {token.token}')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('vinculado a otra cuenta', message)
        self.assertIn('/unlink', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_link_success(self, mock_send):
        """Test successful /link command."""
        mock_send.return_value = {'success': True}

        token = TelegramLinkToken.generate_token(self.user)

        response = self._send_command(123456789, f'/link {token.token}', username='tg_user')

        self.assertEqual(response.status_code, 200)

        # Verify channel created correctly
        channel = TelegramChannel.objects.filter(chat_id=123456789).first()
        self.assertIsNotNone(channel)
        self.assertEqual(channel.user, self.user)
        self.assertTrue(channel.is_verified)
        self.assertEqual(channel.username, 'tg_user')

        # Verify token marked as used
        token.refresh_from_db()
        self.assertTrue(token.used)

        # Verify success message
        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('exitosamente', message)

    # /unlink command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_unlink_not_linked(self, mock_send):
        """Test /unlink when not linked."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/unlink')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('no está vinculado', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_unlink_success(self, mock_send):
        """Test successful /unlink command."""
        mock_send.return_value = {'success': True}

        # Create linked channel
        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        response = self._send_command(123456789, '/unlink')

        self.assertEqual(response.status_code, 200)

        # Channel should be deleted
        self.assertFalse(TelegramChannel.objects.filter(chat_id=123456789).exists())

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('desvinculado', message)

    # /status command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_status_not_linked(self, mock_send):
        """Test /status when not linked."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/status')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('No vinculado', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_status_linked(self, mock_send):
        """Test /status when linked."""
        mock_send.return_value = {'success': True}

        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
            last_sent_at=timezone.now(),
        )

        response = self._send_command(123456789, '/status')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('testuser', message)
        self.assertIn('Activo', message)
        self.assertIn('Verificado', message)

    # /suscripciones command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_suscripciones_not_linked(self, mock_send):
        """Test /suscripciones when not linked."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/suscripciones')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('no está vinculado', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_suscripciones_no_subscriptions(self, mock_send):
        """Test /suscripciones when linked but no subscriptions."""
        mock_send.return_value = {'success': True}

        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        response = self._send_command(123456789, '/suscripciones')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('No tienes suscripciones', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_suscripciones_with_domain_subscription(self, mock_send):
        """Test /suscripciones with domain subscriptions."""
        mock_send.return_value = {'success': True}

        from dominios.models import Dominio, Zona
        from subscriptions.models import SubscriptionTarget, UserSubscription
        from django.contrib.contenttypes.models import ContentType

        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        # Create a domain and subscription
        zona = Zona.objects.create(nombre='ar')
        dominio = Dominio.objects.create(
            nombre='example',
            zona=zona,
        )

        domain_ct = ContentType.objects.get_for_model(Dominio)
        target = SubscriptionTarget.objects.create(
            content_type=domain_ct,
            object_id=dominio.id
        )

        UserSubscription.objects.create(
            user=self.user,
            target=target,
            event_types=['dropped', 'registered'],
            delivery_mode='immediate',
            is_active=True,
        )

        response = self._send_command(123456789, '/suscripciones')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Dominios:', message)
        self.assertIn('example.ar', message)
        self.assertIn('Total:', message)
        self.assertIn('1 suscripciones', message)

    @patch('channels.views.telegram_sender.send_raw_message')
    def test_suscripciones_with_registrant_subscription(self, mock_send):
        """Test /suscripciones with registrant subscriptions."""
        mock_send.return_value = {'success': True}

        from dominios.models import Registrante
        from subscriptions.models import SubscriptionTarget, UserSubscription
        from django.contrib.contenttypes.models import ContentType

        TelegramChannel.objects.create(
            user=self.user,
            chat_id=123456789,
            is_active=True,
            is_verified=True,
        )

        # Create a registrant and subscription
        registrante = Registrante.objects.create(
            name='ACME Corporation',
        )

        registrant_ct = ContentType.objects.get_for_model(Registrante)
        target = SubscriptionTarget.objects.create(
            content_type=registrant_ct,
            object_id=registrante.id
        )

        UserSubscription.objects.create(
            user=self.user,
            target=target,
            event_types=['new_domain'],
            delivery_mode='daily',
            is_active=True,
        )

        response = self._send_command(123456789, '/suscripciones')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Registrantes:', message)
        self.assertIn('ACME Corporation', message)

    # /help command tests
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_help_command(self, mock_send):
        """Test /help command."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/help')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Comandos disponibles', message)
        self.assertIn('/start', message)
        self.assertIn('/link', message)
        self.assertIn('/unlink', message)
        self.assertIn('/status', message)
        self.assertIn('/suscripciones', message)
        self.assertIn('/help', message)

    # Unknown command test
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_unknown_command(self, mock_send):
        """Test unknown command."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/unknowncommand')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('no reconocido', message)
        self.assertIn('/help', message)

    # Edge cases
    @patch('channels.views.telegram_sender.send_raw_message')
    def test_command_with_bot_mention(self, mock_send):
        """Test command with @botname suffix."""
        mock_send.return_value = {'success': True}

        response = self._send_command(123456789, '/help@ArDomNewsBot')

        self.assertEqual(response.status_code, 200)

        call_args = mock_send.call_args
        message = call_args[0][1]
        self.assertIn('Comandos disponibles', message)

    def test_non_command_message_ignored(self):
        """Test that non-command messages don't trigger commands."""
        response = self._send_command(123456789, 'Hello, how are you?')

        self.assertEqual(response.status_code, 200)

    def test_group_chat_ignored(self):
        """Test that group chats are ignored."""
        response = self.client.post(
            '/channels/telegram/webhook/',
            data=json.dumps({
                'message': {
                    'message_id': 100,
                    'chat': {'id': -123456789, 'type': 'group'},
                    'from': {'id': 111, 'first_name': 'Test'},
                    'text': '/start'
                }
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        # No channel should be created for group chats
        self.assertFalse(TelegramChannel.objects.exists())
