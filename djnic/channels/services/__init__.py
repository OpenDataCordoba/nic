"""
Base notification service and registry.

This module provides the base class for notification senders
and a registry to manage different channel types.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from django.utils import timezone

from subscriptions.models import UserNotification
from channels.models import ChannelDelivery


logger = logging.getLogger(__name__)


class NotificationSender(ABC):
    """
    Abstract base class for notification senders.
    Each channel type (Telegram, WebPush, etc.) implements this.
    """

    channel_type: str = None  # Must be set by subclass

    @abstractmethod
    def send(self, channel, notification: UserNotification) -> Dict[str, Any]:
        """
        Send a notification to a specific channel.

        Args:
            channel: The channel model instance (TelegramChannel, etc.)
            notification: The UserNotification to send

        Returns:
            Dict with keys:
                - success: bool
                - external_id: str (optional, e.g., telegram message_id)
                - error: str (optional, error message if failed)
        """
        pass

    @abstractmethod
    def format_message(self, notification: UserNotification) -> str:
        """
        Format the notification content for this channel.

        Args:
            notification: The UserNotification to format

        Returns:
            Formatted message string
        """
        pass

    def get_active_channels(self, user):
        """
        Get all active channels of this type for a user.
        Override in subclass to return the correct model queryset.
        """
        raise NotImplementedError("Subclass must implement get_active_channels")

    def send_to_user(self, user, notification: UserNotification) -> List[ChannelDelivery]:
        """
        Send notification to all active channels of this type for a user.

        Returns list of ChannelDelivery records created.
        """
        deliveries = []
        channels = self.get_active_channels(user)

        for channel in channels:
            delivery = self._send_to_channel(channel, notification)
            deliveries.append(delivery)

        return deliveries

    def _send_to_channel(self, channel, notification: UserNotification) -> ChannelDelivery:
        """
        Send to a single channel and record the delivery.
        """
        # Check if delivery already exists
        delivery, created = ChannelDelivery.objects.get_or_create(
            notification=notification,
            channel_type=self.channel_type,
            channel_id=channel.id,
            defaults={'status': ChannelDelivery.STATUS_PENDING}
        )

        if not created and delivery.status == ChannelDelivery.STATUS_SENT:
            # Already sent successfully
            return delivery

        try:
            result = self.send(channel, notification)

            if result.get('success'):
                delivery.status = ChannelDelivery.STATUS_SENT
                delivery.sent_at = timezone.now()
                delivery.external_id = result.get('external_id', '')
                delivery.error_message = ''

                # Update channel stats
                channel.last_sent_at = timezone.now()
                channel.error_count = 0
                channel.save(update_fields=['last_sent_at', 'error_count'])
            else:
                delivery.status = ChannelDelivery.STATUS_FAILED
                delivery.error_message = result.get('error', 'Unknown error')
                delivery.retry_count += 1

                # Update channel error stats
                channel.last_error_at = timezone.now()
                channel.last_error_message = delivery.error_message
                channel.error_count += 1
                channel.save(update_fields=['last_error_at', 'last_error_message', 'error_count'])

                logger.error(
                    f"Failed to send notification {notification.id} "
                    f"to {self.channel_type} channel {channel.id}: {delivery.error_message}"
                )

        except Exception as e:
            delivery.status = ChannelDelivery.STATUS_FAILED
            delivery.error_message = str(e)
            delivery.retry_count += 1
            logger.exception(
                f"Exception sending notification {notification.id} "
                f"to {self.channel_type} channel {channel.id}"
            )

        delivery.save()
        return delivery


class NotificationRegistry:
    """
    Registry of notification senders by channel type.
    """
    _senders: Dict[str, NotificationSender] = {}

    @classmethod
    def register(cls, sender: NotificationSender):
        """Register a sender for its channel type."""
        if not sender.channel_type:
            raise ValueError("Sender must have channel_type set")
        cls._senders[sender.channel_type] = sender
        logger.info(f"Registered notification sender for {sender.channel_type}")

    @classmethod
    def get_sender(cls, channel_type: str) -> Optional[NotificationSender]:
        """Get the sender for a channel type."""
        return cls._senders.get(channel_type)

    @classmethod
    def get_all_senders(cls) -> Dict[str, NotificationSender]:
        """Get all registered senders."""
        return cls._senders.copy()

    @classmethod
    def send_notification(cls, notification: UserNotification) -> List[ChannelDelivery]:
        """
        Send a notification through all available channels for the user.

        Returns list of all ChannelDelivery records created.
        """
        all_deliveries = []

        for channel_type, sender in cls._senders.items():
            try:
                deliveries = sender.send_to_user(notification.user, notification)
                all_deliveries.extend(deliveries)
            except Exception as e:
                logger.exception(
                    f"Error sending notification {notification.id} via {channel_type}: {e}"
                )

        return all_deliveries
