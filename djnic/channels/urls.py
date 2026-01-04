from django.urls import path
from .views import TelegramWebhookView, setup_telegram_webhook
from .api import (
    generate_telegram_link_token,
    get_telegram_status,
    toggle_telegram_channel,
    unlink_telegram,
)

app_name = 'channels'

urlpatterns = [
    # Telegram webhook endpoint (called by Telegram servers)
    path('telegram/webhook/', TelegramWebhookView.as_view(), name='telegram_webhook'),

    # Admin endpoint to set up webhook (call once during deployment)
    path('telegram/setup-webhook/', setup_telegram_webhook, name='telegram_setup_webhook'),

    # API endpoints for user management
    path('api/telegram/link-token/', generate_telegram_link_token, name='telegram_link_token'),
    path('api/telegram/status/', get_telegram_status, name='telegram_status'),
    path('api/telegram/toggle/', toggle_telegram_channel, name='telegram_toggle'),
    path('api/telegram/unlink/', unlink_telegram, name='telegram_unlink'),
]
