

def calculate_priority(expire_days, readed_days, updated_days, estado):
    """ Calculate the prioriti to update a domain
        expire_days: days since the domain is expired. e.g. -5=will expire in 5 days
        readed_days: days since this domain was readed agains whois
        updated_days: days since this domain eas updated (readed and having changes)
        
        Priority for Argentina """
    
    from dominios.models import STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE

    priority = 0
    # si ya lo leí hace poco, al fondo
    if estado == STATUS_NO_DISPONIBLE:
        if readed_days > 6:
            # en Argentina los dominios caen 45 dias despues de vencidos
            if expire_days > 45 and expire_days < 66:
                priority = 10000000 + (expire_days*10) + (readed_days*5) + updated_days
            elif expire_days > -26 and expire_days < 46:
                priority = 1000000 + (expire_days*2) + (readed_days*5) + updated_days
            elif expire_days > 65 and expire_days < 121:
                priority = 100000 + (expire_days) + readed_days + updated_days
            elif expire_days < -25:
                priority = 10000 + expire_days + readed_days + updated_days
        else:
            priority = readed_days * 3
    else:
        if updated_days < 45:
            priority = readed_days + updated_days
        
    return priority
