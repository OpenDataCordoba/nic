from django.contrib import admin
from django.utils.html import format_html

from .models import TelegramChannel, ChannelDelivery, TelegramLinkToken


@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'telegram_display', 'is_active', 'is_verified',
        'error_count', 'last_sent_at', 'created_at'
    ]
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'username', 'chat_id']
    readonly_fields = ['uid', 'channel_type', 'created_at', 'updated_at', 'last_sent_at', 'last_error_at']
    raw_id_fields = ['user']

    fieldsets = (
        (None, {
            'fields': ('uid', 'user', 'channel_type')
        }),
        ('Telegram Info', {
            'fields': ('chat_id', 'username', 'first_name', 'last_name')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Preferences', {
            'fields': ('parse_mode', 'disable_preview')
        }),
        ('Stats', {
            'fields': ('last_sent_at', 'last_error_at', 'last_error_message', 'error_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def telegram_display(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank">@{}</a>',
                obj.username, obj.username
            )
        return f"Chat {obj.chat_id}"
    telegram_display.short_description = 'Telegram'


@admin.register(ChannelDelivery)
class ChannelDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'notification', 'channel_type', 'status',
        'retry_count', 'sent_at', 'created_at'
    ]
    list_filter = ['status', 'channel_type', 'created_at']
    search_fields = ['notification__title', 'notification__user__username']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    raw_id_fields = ['notification']

    fieldsets = (
        (None, {
            'fields': ('uid', 'notification', 'channel_type', 'channel_id')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message', 'retry_count')
        }),
        ('External', {
            'fields': ('external_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'used', 'expires_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username', 'token']
    readonly_fields = ['uid', 'created_at']
    raw_id_fields = ['user']
