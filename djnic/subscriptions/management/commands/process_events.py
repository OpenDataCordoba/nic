"""
Management command to process Events and create UserNotifications.

This command:
1. Finds all unprocessed Events (processed=False)
2. For each Event, finds matching SubscriptionTargets
3. Finds UserSubscriptions that match the event type
4. Creates UserNotification for each matching subscription
5. Marks the Event as processed

Run via cron, e.g.: */5 * * * * cd /path/to/project && python manage.py process_events
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from subscriptions.models import (
    Event, SubscriptionTarget, UserSubscription, UserNotification
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process unprocessed events and create user notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of events to process (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))

        # Get unprocessed events, oldest first
        events = Event.objects.filter(processed=False).order_by('created_at')[:limit]
        event_count = events.count()

        if event_count == 0:
            self.stdout.write('No unprocessed events found')
            return

        self.stdout.write(f'Processing {event_count} events...')

        notifications_created = 0
        events_processed = 0

        for event in events:
            try:
                created = self.process_event(event, dry_run)
                notifications_created += created
                events_processed += 1

                if not dry_run:
                    event.processed = True
                    event.save(update_fields=['processed'])

            except Exception as e:
                logger.error(f'Error processing event {event.id}: {e}')
                self.stdout.write(
                    self.style.ERROR(f'Error processing event {event.id}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {events_processed} events, '
                f'created {notifications_created} notifications'
            )
        )

    def process_event(self, event, dry_run=False):
        """
        Process a single event and create notifications for matching subscriptions.
        Returns the number of notifications created.
        """
        # Find the SubscriptionTarget for this event's object
        target = SubscriptionTarget.objects.filter(
            content_type=event.content_type,
            object_id=event.object_id
        ).first()

        if not target:
            logger.debug(
                f'No subscription target for {event.content_type} #{event.object_id}'
            )
            return 0

        # Find all active subscriptions for this target
        # that include this event type
        subscriptions = UserSubscription.objects.filter(
            target=target,
            is_active=True
        )

        notifications_created = 0

        for subscription in subscriptions:
            # Check if user is subscribed to this event type
            if event.event_type not in subscription.event_types:
                continue

            # Create notification
            notification_data = self.build_notification(event, subscription)

            if dry_run:
                self.stdout.write(
                    f'  Would notify {subscription.user.username} '
                    f'about {event.event_type} on {target}'
                )
            else:
                notification = UserNotification.objects.create(**notification_data)
                logger.info(
                    f'Created notification {notification.id} for '
                    f'{subscription.user.username}'
                )

            notifications_created += 1

            # Update subscription last_notified_at
            if not dry_run:
                subscription.last_notified_at = timezone.now()
                subscription.save(update_fields=['last_notified_at'])

        # Update target last_event_at
        if not dry_run and notifications_created > 0:
            target.last_event_at = timezone.now()
            target.save(update_fields=['last_event_at'])

        return notifications_created

    def build_notification(self, event, subscription):
        """
        Build notification data from an event.
        """
        event_data = event.event_data or {}

        # Build title from event data
        title = event_data.get('description', f'{event.get_event_type_display()}')

        # Truncate title if too long
        if len(title) > 200:
            title = title[:197] + '...'

        return {
            'user': subscription.user,
            'event': event,
            'notification_type': 'single',
            'title': title,
            'summary': '',
            'event_data': event_data,
            'event_date': event.created_at.date(),
            'is_read': False,
        }
