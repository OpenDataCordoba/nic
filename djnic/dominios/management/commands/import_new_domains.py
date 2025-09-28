import logging
from django.core.management.base import BaseCommand
from dominios.models import PreDominio


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar archivos de texto con posibles dominios nuevos a la base'

    def add_arguments(self, parser):
        parser.add_argument('--path', nargs='?', type=str, help='Path del archivo con los datos (lista simple de texto')
        parser.add_argument('--priority', nargs='?', type=int, default=50)

    def handle(self, *args, **options):
        f = open(options['path'], 'r')
        doms = f.read()
        f.close()
        dlist = doms.split('\n')
        c = 0
        skipped = 0
        for dominio in dlist:
            dominio = dominio.strip().lower()
            c += 1
            self.stdout.write(self.style.SUCCESS(f"{c} [{skipped}] {dominio}"))

            # Ver si existe como dominio
            dominio_obj = PreDominio.get_domain(dominio)
            if dominio_obj is False:
                # bad domain
                skipped += 1
                continue

            if dominio_obj:
                # ya existe como dominio
                skipped += 1
                continue

            # dominio_obj is None -> valid but not exists
            pd, created = PreDominio.objects.get_or_create(dominio=dominio)
            if not created:
                skipped += 1
                continue

            pd.priority = options['priority']
            pd.save()

        self.stdout.write(self.style.SUCCESS(f"DONE. {c} processed {skipped} skipped"))
