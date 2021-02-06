from core.data import get_messages, get_notifications


def core_ctx(request):
    notifications = get_notifications(request.user)
    return {
        'notifications': notifications
    }