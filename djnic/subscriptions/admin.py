from django.contrib import admin
from subscriptions.models import SubscriptionTarget, UserSubscription, Event, UserNotification


@admin.register(SubscriptionTarget)
class SubscriptionTargetAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_type', 'object_id', 'created_at']
    list_filter = ['content_type']
    search_fields = ['object_id']
    readonly_fields = ['uid', 'content_object', 'last_event_at', 'created_at']

    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id', 'content_object')
        }),
        ('Statistics', {
            'fields': ('last_event_at',)
        }),
        ('Metadata', {
            'fields': ('uid', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def content_object(self, obj):
        return str(obj.content_object) if obj.content_object else '-'
    content_object.short_description = 'Target Object'


class UserSubscriptionInline(admin.TabularInline):
    model = UserSubscription
    extra = 0
    readonly_fields = ['uid', 'created_at', 'last_notified_at']
    raw_id_fields = ['user']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'target', 'delivery_mode', 'is_active', 'event_types_display', 'created_at']
    list_filter = ['delivery_mode', 'is_active']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['uid', 'created_at', 'updated_at', 'last_notified_at']
    raw_id_fields = ['user', 'target']
    list_select_related = ['user', 'target']

    fieldsets = (
        (None, {
            'fields': ('user', 'target')
        }),
        ('Preferences', {
            'fields': ('event_types', 'delivery_mode', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uid', 'created_at', 'updated_at', 'last_notified_at'),
            'classes': ('collapse',)
        }),
    )

    def event_types_display(self, obj):
        if obj.event_types:
            return ', '.join(obj.event_types)
        return '-'
    event_types_display.short_description = 'Event Types'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_type', 'content_type', 'object_id', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'content_type']
    search_fields = ['object_id', 'event_data']
    readonly_fields = ['uid', 'content_object', 'created_at']

    fieldsets = (
        (None, {
            'fields': ('event_type', 'content_type', 'object_id', 'content_object')
        }),
        ('Event Details', {
            'fields': ('event_data', 'processed')
        }),
        ('Metadata', {
            'fields': ('uid', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def content_object(self, obj):
        return str(obj.content_object) if obj.content_object else '-'
    content_object.short_description = 'Related Object'

    actions = ['mark_as_processed', 'mark_as_unprocessed']

    @admin.action(description='Mark selected events as processed')
    def mark_as_processed(self, request, queryset):
        queryset.update(processed=True)

    @admin.action(description='Mark selected events as unprocessed')
    def mark_as_unprocessed(self, request, queryset):
        queryset.update(processed=False)


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'notification_type', 'is_read', 'event_date', 'created_at']
    list_filter = ['notification_type', 'is_read', 'event_date']
    search_fields = ['user__username', 'user__email', 'title', 'summary']
    readonly_fields = ['uid', 'created_at']
    raw_id_fields = ['user', 'event']
    date_hierarchy = 'created_at'
    list_select_related = ['user', 'event']

    fieldsets = (
        (None, {
            'fields': ('user', 'event', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'summary', 'event_data', 'grouped_events')
        }),
        ('Status', {
            'fields': ('is_read', 'event_date')
        }),
        ('Metadata', {
            'fields': ('uid', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected notifications as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
