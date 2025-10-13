

def calculate_priority(expire_days, readed_days, updated_days, estado):
    """ Calculate the prioriti to update a domain
        expire_days: days since the domain is expired. e.g. -5=will expire in 5 days
        readed_days: days since this domain was readed agains whois
        updated_days: days since this domain was updated (readed and having changes)

        Priority for Argentina """

    from dominios.models import STATUS_NO_DISPONIBLE

    priority = 0
    # si ya lo leí hace poco, al fondo
    if estado == STATUS_NO_DISPONIBLE:

        # en Argentina los dominios caen 45 dias despues de vencidos
        if expire_days >= 45 and expire_days < 95:
            priority = 10_000_000 + (expire_days*10) + (readed_days*5) + updated_days
        elif expire_days > 94 and expire_days < 365:
            # Demoras nuestras probablemente
            priority = 7_000_000 + (expire_days*5) + (readed_days*5) + updated_days
        elif expire_days > 364 and expire_days < 1530:
            # Demoras nuestras probablemente
            priority = 5_000_000 + (expire_days*2) + (readed_days*5) + updated_days
        elif expire_days > 1529:
            # probablemente judicializados y cosas sin sentido
            priority = 3_000_000 + (expire_days*2) + (readed_days*5) + updated_days
        elif expire_days >= -25 and expire_days < 46:
            priority = 1_000_000 + (expire_days*2) + (readed_days*5) + updated_days
        elif expire_days < -25:
            priority = 10_000 + expire_days + readed_days + updated_days
        else:
            # non expected, a gap in the selecion
            priority = -2

    else:
        priority = (readed_days*10) + updated_days

    return priority
