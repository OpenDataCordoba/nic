import logging
from django.core.management.base import BaseCommand, CommandError

from core.models import News
from dominios.models import PreDominio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualizar datos de dominios desde un archivo de texto llamado news.txt'

    def add_arguments(self, parser):
        parser.add_argument('--sleep', nargs='?', type=int, default=41)

    def handle(self, *args, **options):
        f = open('news.txt', 'r')
        doms = f.read()
        f.close()
        dlist = doms.split('\n')
        
        c = 0
        skipped = 0
        news = 0
        already_domain = 0
        report = '-'

        for dominio in dlist:
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
        
        News.objects.create(title='NEW AR Domains', description=report)
        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed"))
        