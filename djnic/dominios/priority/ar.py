from django.utils import timezone


def calculate_priority(expire_days, readed_days, updated_days, estado):
    """ Calculate the prioriti to update a domain
        expire_days: days since the domain is expired. e.g. -5=will expire in 5 days
        readed_days: days since this domain was readed agains whois
        updated_days: days since this domain was updated (readed and having changes)

        Priority for Argentina """

    from dominios.models import STATUS_NO_DISPONIBLE

    priority = 0
    next_update_priority = timezone.now() + timezone.timedelta(days=15)

    if readed_days <= 3:
        # si lo lei hace poco, darle baja prioridad, estamos leyendo algunas cosas muy seguido
        priority = -4
        next_update_priority = timezone.now() + timezone.timedelta(days=1)
        return priority, next_update_priority

    # si ya lo leí hace poco, al fondo
    if estado == STATUS_NO_DISPONIBLE:

        # en Argentina los dominios caen 45 dias despues de vencidos
        if expire_days >= 46 and expire_days < 95:
            readed_days_pond = (readed_days - 6) * 2_000_000 if readed_days <= 6 else readed_days * 5
            priority = 11_500_000 + (expire_days*10) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=3)
        elif expire_days >= 0 and expire_days < 46:
            # Este es el momento de renovacion, es importante tambien
            readed_days_pond = (readed_days - 10) * 400_000 if readed_days <= 10 else readed_days * 5
            priority = 5_200_000 + (expire_days*2) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=3)
        elif expire_days >= -31 and expire_days < 0:
            # Este es el momento de renovacion, es importante tambien
            readed_days_pond = (readed_days - 10) * 500_000 if readed_days <= 10 else readed_days * 5
            priority = 5_100_000 + (expire_days*2) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=4)
        elif expire_days > 94 and expire_days < 365:
            # Demoras nuestras probablemente
            readed_days_pond = (readed_days - 30) * 200_000 if readed_days <= 30 else readed_days * 5
            priority = 7_000_000 + (expire_days*5) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=7)
        elif expire_days > 364 and expire_days < 1530:
            # Demoras nuestras probablemente
            readed_days_pond = (readed_days - 50) * 100_000 if readed_days <= 50 else readed_days * 5
            priority = 5_000_000 + (expire_days*2) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=15)
        elif expire_days > 1529:
            # probablemente judicializados y cosas sin sentido
            readed_days_pond = (readed_days - 300) * 50_000 if readed_days <= 300 else readed_days * 5
            priority = 3_000_000 + (expire_days*2) + readed_days_pond + updated_days
            next_update_priority = timezone.now() + timezone.timedelta(days=25)
        elif expire_days < -31 and expire_days >= -60:
            # evitar los que expiran en 100 años, no usar (o limitar expire_days) aqui
            priority = 150_000 + (readed_days * 1_000)
            next_update_priority = timezone.now() + timezone.timedelta(days=5)
        elif expire_days < -60:
            # evitar los que expiran en 100 años, no usar (o limitar expire_days) aqui
            priority = 50_000 + (readed_days * 1_000)
            next_update_priority = timezone.now() + timezone.timedelta(days=15)
        else:
            # non expected, a gap in the selecion
            priority = -2

    else:
        # Si el dominio cayo hace poco, darle alguna oportunidad
        # En generar los capturamos con los registros de todos los dias
        priority = (readed_days * 100) + updated_days
        next_update_priority = timezone.now() + timezone.timedelta(days=90)

    return priority, next_update_priority
