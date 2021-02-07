from mensajes.models import MensajeDestinado


def get_messages(user):
    """ Obtener todos los mensajes del usuario para la lista de novedades """
    if user.is_authenticated:
        mensajes = MensajeDestinado.objects.filter(destinatario=user).exclude(estado=MensajeDestinado.DELETED)
    else:
        mensajes = []
    return mensajes


def get_notifications(user):
    """ Obtener los mensajes no leidos del usuario """
    if user.is_authenticated:
        mensajes = MensajeDestinado.objects.filter(
            destinatario=user,
            estado=MensajeDestinado.CREATED
        )
    else:
        mensajes = []
    return mensajes
