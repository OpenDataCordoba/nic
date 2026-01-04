"""
Notification Channels Models

Architecture:
- NotificationChannel: Abstract base model for all channel types
- TelegramChannel: Telegram bot notification settings per user
- (Future) WebPushChannel, EmailChannel, WhatsAppChannel

Each user can have multiple channels configured.
When a UserNotification is created, it gets dispatched to all active channels.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User


class NotificationChannel(models.Model):
    """
    Abstract base model for notification channels.
    Each channel type will inherit from this and add its specific fields.
    """
    CHANNEL_TYPE_TELEGRAM = 'telegram'
    CHANNEL_TYPE_WEBPUSH = 'webpush'
    CHANNEL_TYPE_EMAIL = 'email'
    CHANNEL_TYPE_WHATSAPP = 'whatsapp'

    CHANNEL_TYPE_CHOICES = [
        (CHANNEL_TYPE_TELEGRAM, 'Telegram'),
        (CHANNEL_TYPE_WEBPUSH, 'Web Push'),
        (CHANNEL_TYPE_EMAIL, 'Email'),
        (CHANNEL_TYPE_WHATSAPP, 'WhatsApp'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_channels_%(class)s'
    )
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        editable=False
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this channel is currently active for receiving notifications'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Whether the channel has been verified (e.g., user confirmed via bot)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time a notification was successfully sent'
    )
    last_error_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time sending failed'
    )
    last_error_message = models.TextField(
        blank=True,
        help_text='Last error message if any'
    )
    error_count = models.PositiveIntegerField(
        default=0,
        help_text='Consecutive error count (reset on success)'
    )

    class Meta:
        abstract = True

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        verified = "verified" if self.is_verified else "unverified"
        return f"{self.user.username} - {self.get_channel_type_display()} ({status}, {verified})"

    def save(self, *args, **kwargs):
        # Ensure channel_type is set by subclass
        if not self.channel_type:
            raise ValueError("channel_type must be set by subclass")
        super().save(*args, **kwargs)


class TelegramChannel(NotificationChannel):
    """
    Telegram notification channel.
    Users register by starting a conversation with the bot.
    """
    chat_id = models.BigIntegerField(
        unique=True,
        help_text='Telegram chat ID for sending messages'
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        help_text='Telegram username if available'
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Telegram first name'
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Telegram last name'
    )

    # Preferences specific to Telegram
    parse_mode = models.CharField(
        max_length=20,
        default='HTML',
        choices=[('HTML', 'HTML'), ('Markdown', 'Markdown'), ('MarkdownV2', 'MarkdownV2')],
        help_text='Message formatting mode'
    )
    disable_preview = models.BooleanField(
        default=False,
        help_text='Disable link previews in messages'
    )

    class Meta:
        verbose_name = 'Telegram Channel'
        verbose_name_plural = 'Telegram Channels'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['chat_id']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_type = self.CHANNEL_TYPE_TELEGRAM

    def save(self, *args, **kwargs):
        self.channel_type = self.CHANNEL_TYPE_TELEGRAM
        super().save(*args, **kwargs)

    def get_display_name(self):
        """Return a display name for this Telegram account."""
        if self.username:
            return f"@{self.username}"
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return f"Chat {self.chat_id}"


class ChannelDelivery(models.Model):
    """
    Track delivery status of notifications to each channel.
    Links UserNotification to the actual delivery attempts.
    """
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_SKIPPED = 'skipped'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_SKIPPED, 'Skipped'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Link to the notification
    notification = models.ForeignKey(
        'subscriptions.UserNotification',
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    # Which channel type and ID
    channel_type = models.CharField(
        max_length=20,
        choices=NotificationChannel.CHANNEL_TYPE_CHOICES
    )
    channel_id = models.PositiveIntegerField(
        help_text='ID of the specific channel (TelegramChannel.id, etc.)'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    # Delivery details
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    external_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='External message ID (e.g., Telegram message_id)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Channel Delivery'
        verbose_name_plural = 'Channel Deliveries'
        unique_together = ('notification', 'channel_type', 'channel_id')
        indexes = [
            models.Index(fields=['status', 'channel_type']),
            models.Index(fields=['notification', 'status']),
        ]

    def __str__(self):
        return f"{self.notification_id} -> {self.channel_type} ({self.status})"


class TelegramLinkToken(models.Model):
    """
    Temporary token for linking Telegram account to user.
    User gets a token from the web, then sends it to the bot to link accounts.
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['token', 'used']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    @classmethod
    def generate_token(cls, user, expiry_minutes=30):
        """Generate a new link token for a user."""
        import secrets
        from django.utils import timezone
        from datetime import timedelta

        # Invalidate any existing unused tokens
        cls.objects.filter(user=user, used=False).update(used=True)

        token = secrets.token_urlsafe(12)[:16].upper()
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """Check if token is still valid."""
        from django.utils import timezone
        return not self.used and self.expires_at > timezone.now()


class TelegramMessage(models.Model):
    """
    Registro de mensajes intercambiados con el bot de Telegram.
    Guarda tanto mensajes entrantes (del usuario) como salientes (del bot).
    """
    DIRECTION_IN = 'in'
    DIRECTION_OUT = 'out'

    DIRECTION_CHOICES = [
        (DIRECTION_IN, 'Recibido'),
        (DIRECTION_OUT, 'Enviado'),
    ]

    channel = models.ForeignKey(
        TelegramChannel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        help_text='Canal vinculado (puede ser null si el usuario no está vinculado)'
    )
    chat_id = models.BigIntegerField(
        db_index=True,
        help_text='Telegram chat ID (guardado aunque no haya channel)'
    )
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        db_index=True
    )
    text = models.TextField(
        blank=True,
        help_text='Contenido del mensaje'
    )
    telegram_message_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='ID del mensaje en Telegram'
    )
    raw_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Update completo de Telegram (solo para mensajes entrantes)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram Message'
        verbose_name_plural = 'Telegram Messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chat_id', 'created_at']),
            models.Index(fields=['channel', 'created_at']),
        ]

    def __str__(self):
        direction_arrow = '→' if self.direction == self.DIRECTION_OUT else '←'
        text_preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"{direction_arrow} {self.chat_id}: {text_preview}"
