from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from mensajes.models import Mensaje, MensajeDestinado


class Command(BaseCommand):
    help = 'Create test messages'

    def handle(self, *args, **options):

        users = User.objects.all()
        now = timezone.now()
        html = '''
            <img src="https://www.himgs.com/imagenes/hello/common/hello-logo-solo.svg" 
                 style="max-width:40%; padding:15px; float:left" />
            Internal <b>Text message</b> {now}
            '''
        msg1 = Mensaje.objects.create(titulo=f'Unread at {now}', texto=html)
        msg2 = Mensaje.objects.create(titulo=f'Readed at {now}', texto=f'Internal <b>Text message</b> {now}')
        msg3 = Mensaje.objects.create(titulo=f'Deleted at {now}', texto=f'Internal <b>Text message</b> {now}')

        for user in users:
            md = MensajeDestinado.objects.create(mensaje=msg1, destinatario=user)
            md = MensajeDestinado.objects.create(mensaje=msg2, destinatario=user, estado=MensajeDestinado.READED)
            md = MensajeDestinado.objects.create(mensaje=msg3, destinatario=user, estado=MensajeDestinado.DELETED)
            
            self.stdout.write(self.style.SUCCESS(f"Created {md}"))
