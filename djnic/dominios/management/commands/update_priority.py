import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from dominios.models import Dominio
from core.models import News


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar prioridad en los dominios'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=25000)

    def handle(self, *args, **options):

        dominios = Dominio.objects.filter(next_update_priority__lt=timezone.now())
        # order to process older first
        dominios = dominios.order_by('next_update_priority')
        limit = options['limit']
        if limit:
            dominios = dominios[:limit]

        c = 0
        for dominio in dominios:
            c += 1
            old_up = dominio.next_update_priority
            old_npu = dominio.priority_to_update
            dominio.calculate_priority()
            self.stdout.write(self.style.SUCCESS(
                f"{c} - {dominio} \n\t({old_npu} {old_up}) => ({dominio.next_update_priority} {dominio.priority_to_update})")
            )

        report = f"{c} processed"
        self.stdout.write(self.style.SUCCESS(report))
        News.objects.create(title='Update priority', description=report)
