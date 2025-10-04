import logging
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from dominios.models import Dominio
from core.models import News


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar prioridad en los dominios'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=25000)
        # --all to review ALL domains
        parser.add_argument('--all', action='store_true', help='Review ALL domains')
        parser.add_argument('--chunk-size', nargs='?', type=int, default=1000, help='Chunk size for pagination')

    def handle(self, *args, **options):

        all = options['all']
        chunk_size = options['chunk_size']

        if all:
            dominios = Dominio.objects.all()
        else:
            dominios = Dominio.objects.filter(next_update_priority__lt=timezone.now())
        # order to process older first
        dominios = dominios.order_by('next_update_priority')
        limit = options['limit']
        if limit:
            dominios = dominios[:limit]

        c = 0
        from_0_to_any = 0
        old_nup = None

        # Use iterator with chunking to avoid loading all records into memory
        for dominio in dominios.iterator(chunk_size=chunk_size):
            c += 1
            old_nup = dominio.next_update_priority
            old_ptu = dominio.priority_to_update
            dominio.calculate_priority()
            self.stdout.write(
                self.style.SUCCESS(
                    f"{c} - {dominio} \n\t"
                    f"Expire: {dominio.expire}\n\t"
                    f"{old_nup} => {dominio.next_update_priority}\n\t"
                    f"{old_ptu} => {dominio.priority_to_update}"
                )
            )
            if old_ptu == 0 and dominio.priority_to_update > 0:
                from_0_to_any += 1
            # sleep every 3000
            if c and c % 3000 == 0:
                time.sleep(4)

        report = f"{c} processed, {from_0_to_any} from 0 to any. Latest NPU: {old_nup}"
        self.stdout.write(self.style.SUCCESS(report))
        News.objects.create(title='Update priority', description=report)
