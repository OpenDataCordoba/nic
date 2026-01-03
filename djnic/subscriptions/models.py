import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


EVENT_TYPE_CHOICES = [
        ('registered', 'Dominio Registerado'),
        ('renewed', 'Dominio Renovado'),
        ('expired', 'Dominio Expirado'),
        ('dropped', 'Dominio Caido'),
        ('dns_changed', 'DNS Cambiado'),
        ('registrant_changed', 'Registrante Cambiado'),
    ]


class SubscriptionTarget(models.Model):
    """
    Represents something that can be subscribed to.
    Uses GenericForeignKey to point to any model: Dominio, Registrante, DNS, Lista, etc.
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_event_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_event_at']
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return f"{self.content_object}"


class UserSubscription(models.Model):
    """
    A user's subscription to a target with their preferences.
    """
    DELIVERY_MODE_CHOICES = [
        ('immediate', 'Immediato'),
        ('daily', 'Mi resumen diario'),
        ('weekly', 'Mi resumen semanal'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    target = models.ForeignKey(
        SubscriptionTarget,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    event_types = models.JSONField(
        default=list,
        help_text='List of event types to subscribe to: ["dropped", "registered", ...]'
    )
    delivery_mode = models.CharField(
        max_length=20,
        choices=DELIVERY_MODE_CHOICES,
        default='immediate'
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'target')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['delivery_mode']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.target}"


class Event(models.Model):
    """
    An event that occurred in the system.
    Events are created when domains change, drop, register, etc.
    """

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, db_index=True)

    # The object this event is about (usually a Dominio)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional event data
    event_data = models.JSONField(
        default=dict,
        help_text='Additional data about the event'
    )

    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether notifications have been generated for this event'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['processed', 'event_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.content_object} at {self.occurred_at}"


class UserNotification(models.Model):
    """
    A notification in the user's feed.
    Can be a single event notification or a digest of multiple events.
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('single', 'Single Event'),
        ('digest', 'Digest'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        help_text='The event this notification is about (null for digests)'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='single'
    )
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    event_data = models.JSONField(
        default=dict,
        help_text='Relevant data for display'
    )
    grouped_events = models.JSONField(
        default=list,
        help_text='List of event IDs if this is a digest'
    )

    is_read = models.BooleanField(default=False, db_index=True)
    event_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of the event(s) for grouping'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        status = "read" if self.is_read else "unread"
        return f"{self.user.username}: {self.title} ({status})"
