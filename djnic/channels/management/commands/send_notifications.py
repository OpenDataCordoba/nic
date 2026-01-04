"""
Management command to send pending notifications through all channels.

This command:
1. Finds UserNotifications that haven't been delivered to all channels
2. For each notification, sends to all active channels for the user
3. Creates ChannelDelivery records to track status

Run via cron, e.g.: */1 * * * * cd /path/to/project && python manage.py send_notifications
"""
import logging
from django.core.management.base import BaseCommand
from django.db.models import Q, Exists, OuterRef

from subscriptions.models import UserNotification
from channels.models import ChannelDelivery, TelegramChannel
from channels.services import NotificationRegistry
# Import to register the sender
from channels.services.telegram import telegram_sender  # noqa


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send pending notifications through all configured channels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of notifications to process (default: 100)'
        )
        parser.add_argument(
            '--channel',
            type=str,
            choices=['telegram', 'webpush', 'email', 'whatsapp'],
            help='Only send via specific channel type'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without sending'
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry previously failed deliveries'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum retry attempts for failed deliveries (default: 3)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        channel_filter = options['channel']
        dry_run = options['dry_run']
        retry_failed = options['retry_failed']
        max_retries = options['max_retries']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No notifications will be sent'))

        # Get notifications that need delivery
        notifications = self.get_pending_notifications(
            limit=limit,
            retry_failed=retry_failed,
            max_retries=max_retries
        )

        if not notifications:
            self.stdout.write('No pending notifications found')
            return

        self.stdout.write(f'Processing {len(notifications)} notifications...')

        sent_count = 0
        failed_count = 0

        senders = NotificationRegistry.get_all_senders()
        if channel_filter:
            senders = {k: v for k, v in senders.items() if k == channel_filter}

        for notification in notifications:
            for channel_type, sender in senders.items():
                try:
                    if dry_run:
                        channels = sender.get_active_channels(notification.user)
                        for channel in channels:
                            self.stdout.write(
                                f"  Would send notification {notification.id} "
                                f"to {channel_type} channel {channel.id}"
                            )
                    else:
                        deliveries = sender.send_to_user(notification.user, notification)
                        for delivery in deliveries:
                            if delivery.status == ChannelDelivery.STATUS_SENT:
                                sent_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Sent notification {notification.id} "
                                        f"via {channel_type}"
                                    )
                                )
                            elif delivery.status == ChannelDelivery.STATUS_FAILED:
                                failed_count += 1
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"Failed notification {notification.id} "
                                        f"via {channel_type}: {delivery.error_message}"
                                    )
                                )

                except Exception as e:
                    logger.exception(f"Error processing notification {notification.id}")
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error processing notification {notification.id}: {e}"
                        )
                    )
                    failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Completed: {sent_count} sent, {failed_count} failed'
            )
        )

    def get_pending_notifications(self, limit, retry_failed, max_retries):
        """
        Get notifications that need delivery.

        A notification needs delivery if:
        1. User has active channels AND
        2. Either no delivery record exists for that channel type, OR
        3. (if retry_failed) delivery failed and retry_count < max_retries
        """
        # Get users with active Telegram channels
        users_with_telegram = TelegramChannel.objects.filter(
            is_active=True,
            is_verified=True
        ).values_list('user_id', flat=True)

        # Base query: notifications for users with active channels
        notifications = UserNotification.objects.filter(
            user_id__in=users_with_telegram
        )

        if retry_failed:
            # Include notifications that have failed deliveries under retry limit
            notifications = notifications.filter(
                Q(deliveries__isnull=True) |  # No delivery attempted
                Q(
                    deliveries__status=ChannelDelivery.STATUS_PENDING
                ) |
                Q(
                    deliveries__status=ChannelDelivery.STATUS_FAILED,
                    deliveries__retry_count__lt=max_retries
                )
            ).distinct()
        else:
            # Only notifications without successful delivery to telegram
            has_telegram_delivery = ChannelDelivery.objects.filter(
                notification=OuterRef('pk'),
                channel_type='telegram',
                status=ChannelDelivery.STATUS_SENT
            )
            notifications = notifications.annotate(
                has_delivery=Exists(has_telegram_delivery)
            ).filter(has_delivery=False)

        return notifications.order_by('created_at')[:limit]
