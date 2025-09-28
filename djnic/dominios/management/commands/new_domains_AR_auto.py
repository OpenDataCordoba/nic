from datetime import date, timedelta
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import News
from dominios.models import PreDominio, STATUS_DISPONIBLE

from whoare.zone_parsers.ar.news_from_blockchain import NewDomains


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Obtener los nuevos dominios de los ultimos días y procesarlos'

    def add_arguments(self, parser):
        parser.add_argument('--days_ago', nargs='?', type=int, default=3)

    def handle(self, *args, **options):

        days_ago = options['days_ago']
        nd = NewDomains()
        nd.data_path = settings.STATIC_ROOT

        fromd = date.today() - timedelta(days=days_ago)
        dominios = nd.get_from_date_range(from_date=fromd, to_date=date.today() - timedelta(days=1))

        c = 0
        skipped = 0
        news = 0
        already_domain = 0
        report = '-'

        for dominio in dominios:
            c += 1

            # Ver si existe como dominio
            dominio_obj = PreDominio.get_domain(dominio)
            if dominio_obj is False:
                # bad domain
                skipped += 1
                continue

            if dominio_obj:
                # ya existe como dominio
                already_domain += 1
                # If is an "available" domain, we suspect it could be re-registered
                # so we give it some priority
                if dominio_obj.estado == STATUS_DISPONIBLE:
                    dominio_obj.priority_to_update += 100000
                    # podriamos perder esto cuando se actualice la prioridad, la pateamos
                    dominio_obj.next_update_priority = timezone.now() + timedelta(days=10)
                    dominio_obj.save()
                    logger.info(f'Available domain {dominio} found as domain, priority updated')
                continue

            # dominio_obj is None -> valid but not exists
            pd, created = PreDominio.objects.get_or_create(dominio=dominio)
            if not created:
                skipped += 1
                # le damos otra oportunidad
                pd.priority += 5
                pd.save()
                continue

            pd.priority = 80
            pd.save()
            news += 1

            report = f'{c} processed. {news} news, {skipped} skipped, {already_domain} already exists as domain'
            self.stdout.write(self.style.SUCCESS(report))

        News.objects.create(title='NEW AR Domains', description=report)
        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed"))
