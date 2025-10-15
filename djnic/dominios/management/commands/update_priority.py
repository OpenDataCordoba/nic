import logging
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from dominios.models import Dominio
from core.models import News
from dominios.models import STATUS_NO_DISPONIBLE


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar prioridad en los dominios'

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='?', type=int, default=25000)
        # --all to review ALL domains
        parser.add_argument('--all', action='store_true', help='Review ALL domains')
        parser.add_argument('--chunk-size', nargs='?', type=int, default=500, help='Chunk size for pagination')
        parser.add_argument('--sleep-interval', nargs='?', type=int, default=2300, help='Sleep every N records')
        parser.add_argument('--sleep-time', nargs='?', type=float, default=4.0, help='Sleep duration in seconds')
        parser.add_argument('--bulk-size', nargs='?', type=int, default=500, help='Bulk update size')
        parser.add_argument('--order-by', nargs='?', type=str, default='next_update_priority', help='Field to order by')
        # only non available flag
        parser.add_argument('--non-available', action='store_true', help='Only process non-available domains')

    def handle(self, *args, **options):

        all = options['all']
        chunk_size = options['chunk_size']
        sleep_interval = options['sleep_interval']
        sleep_time = options['sleep_time']
        bulk_size = options['bulk_size']
        order_by = options['order_by']  
        non_available = options['non_available']

        if all:
            dominios = Dominio.objects.all()
        else:
            dominios = Dominio.objects.filter(next_update_priority__lt=timezone.now())

        if non_available:
            dominios = dominios.filter(estado=STATUS_NO_DISPONIBLE)
        # order to process older first
        dominios = dominios.order_by(order_by)
        limit = options['limit']
        if limit:
            dominios = dominios[:limit]

        c = 0
        from_0_to_any = 0
        old_nup = None
        bulk_updates = []

        # Use iterator with chunking to avoid loading all records into memory
        for dominio in dominios.iterator(chunk_size=chunk_size):
            c += 1
            old_nup = dominio.next_update_priority
            old_ptu = dominio.priority_to_update

            # Calculate priority without saving
            dominio.calculate_priority(save=False)

            # Add to bulk update list
            bulk_updates.append(dominio)

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

            # Bulk update when we reach bulk_size
            if len(bulk_updates) >= bulk_size:
                Dominio.objects.bulk_update(
                    bulk_updates,
                    ['priority_to_update', 'next_update_priority', 'extras']
                )
                self.stdout.write(f"Bulk updated {len(bulk_updates)} records")
                bulk_updates = []
                time.sleep(sleep_time)

            # More frequent sleep to reduce DB load
            if c % sleep_interval == 0:
                time.sleep(sleep_time)
                self.stdout.write(f"Processed {c} records, sleeping {sleep_time}s...")

        # Final bulk update for remaining records
        if bulk_updates:
            Dominio.objects.bulk_update(
                bulk_updates,
                ['priority_to_update', 'next_update_priority', 'extras']
            )
            self.stdout.write(f"Final bulk updated {len(bulk_updates)} records")

        report = f"{c} processed, {from_0_to_any} from 0 to any. Latest NPU: {old_nup}"
        self.stdout.write(self.style.SUCCESS(report))
        News.objects.create(title='Update priority', description=report)
