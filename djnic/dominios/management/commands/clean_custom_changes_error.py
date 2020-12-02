from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dominios.models import Dominio
from cambios.models import CambiosDominio
from core.models import News


class Command(BaseCommand):
    help = 'Deal with some extrange error'

    def add_arguments(self, parser):
        parser.add_argument('--delete', nargs='?', type=bool, default=False)
        parser.add_argument('--days_ago', nargs='?', type=int, default=2)

    def handle(self, *args, **options):
        from_date = timezone.now() - timedelta(days=options['days_ago'])
        changes = CambiosDominio.objects.filter(momento__gt=from_date)
        c = 0
        fix1 = 0
        fix2 = 0
        fix3 = 0
        delete = options['delete']
        for change in changes:
            c += 1
            self.stdout.write(self.style.SUCCESS(f"{c} checking change {change}"))
            if change.campos.count() >= 2:
                rch = None  # reg changed
                rcr = None  # reg created
                for cambio in change.campos.all():
                    self.stdout.write(self.style.SUCCESS(f"{c} checking campo {cambio}"))
                    if cambio.campo == 'registrant_changed':
                        rch = cambio
                    if cambio.campo == 'registrant_created':
                        rcr = cambio

                if rch is not None and rcr is not None:
                    if rch.anterior == rcr.nuevo and rch.nuevo == rcr.anterior:
                        if delete:
                            fix1 += 1
                            self.stdout.write(self.style.ERROR(f" ERROR 1 found {change}\n\t{rcr}\n\t{rch}"))
                            rch.delete()
                            rcr.delete()
                            if change.campos.count() == 2:
                                change.have_changes = False
                                change.save()
                        else:
                            self.stdout.write(self.style.ERROR(f" ERROR 1 found (not changed) {change}\n\t{rcr}\n\t{rch}"))
                    elif rch.anterior == rcr.nuevo:
                        if delete:
                            fix2 += 1
                            self.stdout.write(self.style.ERROR(f" ERROR 2 found {change}\n\t{rcr}\n\t{rch}"))
                            rch.anterior = rcr.anterior
                            rch.save()
                            rcr.delete()
                        else:
                            self.stdout.write(self.style.ERROR(f" ERROR 2 found (not changed) {change}\n\t{rcr}\n\t{rch}"))
                    elif rch.nuevo == rcr.anterior:
                        if delete:
                            fix3 += 1
                            self.stdout.write(self.style.ERROR(f" ERROR 3 found {change}\n\t{rcr}\n\t{rch}"))
                            rcr.anterior = rch.anterior
                            rcr.save()
                            rch.delete()
                        else:
                            self.stdout.write(self.style.ERROR(f" ERROR 3 found (not changed) {change}\n\t{rcr}\n\t{rch}"))
                    
        report = f"{c} processed. Fixes: {fix1}{fix2}{fix3}"
        self.stdout.write(self.style.SUCCESS(report))
        News.objects.create(title='NEW AR Domains', description=report)
        
        
