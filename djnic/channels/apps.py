from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'channels'
    verbose_name = 'Notification Channels'

    def ready(self):
        # Import signals if needed in the future
        pass
