from mensajes.data import get_notifications


def core_ctx(request):
    notifications = get_notifications(request.user)
    return {
        'notifications': notifications
    }