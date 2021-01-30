from analytics.models import Analytic


class AnalyticsViewMixin:
    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            user = request.user
            path = request.path.strip('/').split('/')[-1:][0]
            Analytic.objects.create(
                evento='view',
                user=user,
                referencia=path,
                extras=Analytic.request_as_dict(request)
            )
        return super().get(request, *args, **kwargs)
