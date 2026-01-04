"""
Tests for the channels app.
"""
import json
from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from channels.models import (
    TelegramChannel, TelegramLinkToken, ChannelDelivery, NotificationChannel
)
from channels.services import NotificationRegistry
from channels.services.telegram import TelegramSender
from subscriptions.models import UserNotification, Event
from django.contrib.contenttypes.models import ContentType


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
