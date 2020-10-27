from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dominios.models import Dominio
from cambios.models import CambiosDominio


class Command(BaseCommand):
    help = 'Deal with some extrange error'

    def add_arguments(self, parser):
        parser.add_argument('--delete', nargs='?', type=bool, default=False)

    def handle(self, *args, **options):
        changes = CambiosDominio.objects.filter(momento__gt=datetime(2020, 10, 26, 6, 32))
        c = 0
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
                            self.stdout.write(self.style.ERROR(f" ERROR 2 found {change}\n\t{rcr}\n\t{rch}"))
                            rch.anterior = rcr.anterior
                            rch.save()
                            rcr.delete()
                        else:
                            self.stdout.write(self.style.ERROR(f" ERROR 2 found (not changed) {change}\n\t{rcr}\n\t{rch}"))
                    elif rch.nuevo == rcr.anterior:
                        if delete:
                            self.stdout.write(self.style.ERROR(f" ERROR 3 found {change}\n\t{rcr}\n\t{rch}"))
                            rcr.anterior = rch.anterior
                            rcr.save()
                            rch.delete()
                        else:
                            self.stdout.write(self.style.ERROR(f" ERROR 3 found (not changed) {change}\n\t{rcr}\n\t{rch}"))
                    
        self.stdout.write(self.style.SUCCESS(f"{c} processed"))
        