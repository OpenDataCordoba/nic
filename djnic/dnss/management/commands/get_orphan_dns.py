from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from dnss.models import DNS
from dominios.models import Dominio, STATUS_NO_DISPONIBLE

class Command(BaseCommand):
    help = 'Buscar DNSs que no pertenezcan a una empresa'

    def add_arguments(self, parser):
        parser.add_argument('--show', nargs='?', type=int, default=30)
        parser.add_argument('--show_domains', nargs='?', type=int, default=0)

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS("Buscando DNSs"))
        orphans = DNS.objects.filter(empresa_regex__isnull=True)
        pending = orphans.annotate(total_dominios=Count('dominios', filter=Q(dominios__orden=1))).order_by('total_dominios')
        
        process = pending[:options['show']]

        for p in process:
            self.stdout.write(self.style.WARNING(f'{p.dominio} {p.total_dominios}'))
            if options['show_domains'] > 0:
                dominios = Dominio.objects.filter(estado=STATUS_NO_DISPONIBLE)\
                        .filter(dnss__dns=p)[:options['show_domains']]
                for d in dominios:
                    self.stdout.write(self.style.WARNING(f' - {d}'))
            
        self.stdout.write(self.style.SUCCESS(f"FIN {pending.count()} pending"))
