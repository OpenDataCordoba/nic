from datetime import date, timedelta
import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import News
from dominios.models import PreDominio

from whoare.zone_parsers.ar.news import NewDomains


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
        dominios = nd.get_from_date_range(from_date=fromd)

        c = 0
        skipped = 0
        news = 0
        already_domain = 0
        report = '-'

        for dominio in dominios:
            c += 1
            
            pd, created = PreDominio.objects.get_or_create(dominio=dominio)
            # ID=0 si ya existe como dominio
            if not created:
                skipped += 1
                continue
            
            if pd.id == 0:
                already_domain += 1
            else:
                pd.priority=80
                pd.save()
                news += 1

            report = f'{c} processed. {news} news, {skipped} skipped, {already_domain} already exists as domain'
            self.stdout.write(self.style.SUCCESS(report))
        
        News.objects.create(title='Clean failed changes', description=report)
        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed"))
        