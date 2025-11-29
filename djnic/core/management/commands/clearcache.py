from django.core.management.base import BaseCommand
from django.core.cache import caches


class Command(BaseCommand):
    help = "Clear all configured Django caches."

    def handle(self, *args, **options):
        for name in caches:
            caches[name].clear()
            self.stdout.write(self.style.SUCCESS(f"Cleared cache: {name}"))
