import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from dominios.models import Dominio
from core.models import News


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar prioridad en los dominios'

    def add_arguments(self, parser):
        parser.add_argument('--force', nargs='?', type=bool, default=False)

    def handle(self, *args, **options):

        dominios = Dominio.objects.filter(next_update_priority__lt=timezone.now())
        # order to process older first
        dominios = dominios.order_by('next_update_priority')
        if dominios.count() > 25000:
            dominios = Dominio.objects.order_by('next_update_priority')[:25000]

        c = 0
        for dominio in dominios:
            c += 1
            old_up = dominio.next_update_priority
            dominio.calculate_priority()
            self.stdout.write(self.style.SUCCESS(
                f"{c} {dominio.priority_to_update} {old_up} => {dominio.next_update_priority} {dominio}")
            )

        report = f"{c} processed"
        self.stdout.write(self.style.SUCCESS(report))
        News.objects.create(title='Update priority', description=report)
