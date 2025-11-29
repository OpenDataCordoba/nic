from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if settings.DEBUG:
            try:
                from allauth.socialaccount.models import SocialApp
                from django.contrib.sites.models import Site
                site, _ = Site.objects.get_or_create(pk=1, defaults={'domain': 'example.com', 'name': 'example.com'})
                # GitHub
                app, _ = SocialApp.objects.get_or_create(
                    provider='github',
                    name='GitHub',
                    defaults={'client_id': 'client', 'secret': 'secret'}
                )
                app.sites.add(site)
                # Google
                app, _ = SocialApp.objects.get_or_create(
                    provider='google',
                    name='Google',
                    defaults={'client_id': 'client', 'secret': 'secret'}
                )
                app.sites.add(site)
            except Exception:
                pass
