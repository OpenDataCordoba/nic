from django.test.runner import DiscoverRunner


class CustomTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)

        # Create SocialApp
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        # Ensure Site exists
        site, _ = Site.objects.get_or_create(pk=1, defaults={'domain': 'example.com', 'name': 'example.com'})

        # Create GitHub app
        app, _ = SocialApp.objects.get_or_create(provider='github', name='GitHub', client_id='client', secret='secret')
        app.sites.add(site)

        # Create Google app
        app, _ = SocialApp.objects.get_or_create(provider='google', name='Google', client_id='client', secret='secret')
        app.sites.add(site)

        return result
