"""
Service for creating subscription events from domain changes.

In Argentina (.ar domains):
- When a domain reaches its 'expire' date, it does NOT drop immediately
- The domain continues working for ~15 more days after expiration
- Only when the status changes from 'no disponible' to 'disponible' does the domain actually drop
- The 'expire' date change (extension) indicates a renewal

Events are created for:
1. The domain itself (so subscribers to the domain get notified)
2. The registrant(s) involved (so subscribers to registrants get notified)
"""
import logging
from django.contrib.contenttypes.models import ContentType
from subscriptions.models import (
    Event, EVENT_DROPPED, EVENT_REGISTERED, EVENT_RENEWED,
    EVENT_REGISTRANT_CHANGED, EVENT_DNS_CHANGED
)


logger = logging.getLogger(__name__)


def register_events(dominio, cambios):
    """
    Main entry point to register all events from domain changes.
    Creates events for both the domain and related registrants.
    """
    if not cambios:
        return []

    old_registrante, new_registrante = get_related_registrantes_from_cambios(cambios)

    # Create events for the domain
    domain_events = create_domain_events(
        dominio=dominio,
        cambios=cambios,
        old_registrante=old_registrante,
        new_registrante=new_registrante
    )

    # Create events for registrants
    registrant_events = create_registrant_events(
        dominio=dominio,
        cambios=cambios,
        old_registrante=old_registrante,
        new_registrante=new_registrante,
        current_registrante=dominio.registrante
    )

    return domain_events + registrant_events


def create_domain_events(dominio, cambios, old_registrante=None, new_registrante=None):
    """
    Create Event records for the domain itself.
    """
    created_events = []
    ct_dominio = ContentType.objects.get_for_model(dominio)
    created_types = set()

    for cambio in cambios:
        campo = cambio['campo']
        anterior = cambio['anterior']
        nuevo = cambio['nuevo']

        event_type = None
        event_data = {
            'domain': dominio.full_domain(),
            'url': dominio.get_absolute_url(),
            'campo': campo,
            'anterior': anterior,
            'nuevo': nuevo
        }

        if campo == 'estado':
            if anterior == 'no disponible' and nuevo == 'disponible':
                event_type = EVENT_DROPPED
                event_data['description'] = f'El dominio {dominio.full_domain()} cayó y está disponible'
            elif anterior == 'disponible' and nuevo == 'no disponible':
                event_type = EVENT_REGISTERED
                event_data['description'] = f'El dominio {dominio.full_domain()} fue registrado'

        elif campo == 'registrant_legal_uid':
            event_type = EVENT_REGISTRANT_CHANGED
            event_data['old_registrante_id'] = old_registrante.id if old_registrante else None
            event_data['old_registrante_name'] = old_registrante.name if old_registrante else None
            event_data['old_registrante_url'] = old_registrante.get_absolute_url() if old_registrante else None
            event_data['new_registrante_id'] = new_registrante.id if new_registrante else None
            event_data['new_registrante_name'] = new_registrante.name if new_registrante else None
            event_data['new_registrante_url'] = new_registrante.get_absolute_url() if new_registrante else None
            event_data['description'] = f'El dominio {dominio.full_domain()} cambió de registrante'

        elif campo == 'dominio_expire':
            if anterior and nuevo:
                if nuevo > anterior:
                    event_type = EVENT_RENEWED
                    event_data['description'] = f'El dominio {dominio.full_domain()} fue renovado hasta {nuevo}'
                else:
                    event_type = EVENT_RENEWED
                    event_data['description'] = (
                        f'El dominio {dominio.full_domain()} cambió su fecha '
                        f'de expiración para atras (?) a {nuevo}'
                    )

        elif campo.startswith('DNS'):
            if EVENT_DNS_CHANGED not in created_types:
                event_type = EVENT_DNS_CHANGED
                event_data['description'] = f'El dominio {dominio.full_domain()} cambió sus DNS'

        if event_type and event_type not in created_types:
            event = Event.objects.create(
                event_type=event_type,
                content_type=ct_dominio,
                object_id=dominio.id,
                event_data=event_data
            )
            created_events.append(event)
            created_types.add(event_type)
            logger.info(f'Created domain event {event_type} for {dominio.full_domain()}')

    return created_events


def create_registrant_events(dominio, cambios, old_registrante, new_registrante, current_registrante):
    """
    Create Event records for registrants involved in domain changes.

    - dropped: event for the registrant who lost the domain
    - registered: event for the registrant who got the domain
    - renewed: event for the current registrant
    - registrant_changed: event for old (lost domain) and new (got domain) registrants
    - dns_changed: event for the current registrant
    """
    from registrantes.models import Registrante

    created_events = []
    ct_registrante = ContentType.objects.get_for_model(Registrante)

    # Track what events we've created for each registrant to avoid duplicates
    created_for_registrant = {}  # {registrante_id: set(event_types)}

    for cambio in cambios:
        campo = cambio['campo']
        anterior = cambio['anterior']
        nuevo = cambio['nuevo']

        if campo == 'estado':
            if anterior == 'no disponible' and nuevo == 'disponible':
                # Domain dropped - notify the registrant who had it
                # Note: When domain drops, dominio.registrante might already be None
                # We need to use old_registrante if available, otherwise current
                registrant_to_notify = old_registrante or current_registrante
                if registrant_to_notify:
                    _create_registrant_event(
                        created_events, created_for_registrant, ct_registrante,
                        registrant_to_notify, EVENT_DROPPED,
                        {
                            'domain': dominio.full_domain(),
                            'url': registrant_to_notify.get_absolute_url(),
                            'domain_url': dominio.get_absolute_url(),
                            'description': f'El dominio {dominio.full_domain()} de {registrant_to_notify.name} cayó'
                        }
                    )

            elif anterior == 'disponible' and nuevo == 'no disponible':
                # Domain registered - notify the new registrant
                registrant_to_notify = new_registrante or current_registrante
                if registrant_to_notify:
                    _create_registrant_event(
                        created_events, created_for_registrant, ct_registrante,
                        registrant_to_notify, EVENT_REGISTERED,
                        {
                            'domain': dominio.full_domain(),
                            'url': registrant_to_notify.get_absolute_url(),
                            'domain_url': dominio.get_absolute_url(),
                            'description': f'{registrant_to_notify.name} registró el dominio {dominio.full_domain()}'
                        }
                    )

        elif campo == 'registrant_legal_uid':
            # Registrant changed - notify both old and new
            if old_registrante:
                _create_registrant_event(
                    created_events, created_for_registrant, ct_registrante,
                    old_registrante, EVENT_DROPPED,  # Lost domain = like dropped for them
                    {
                        'domain': dominio.full_domain(),
                        'url': old_registrante.get_absolute_url(),
                        'domain_url': dominio.get_absolute_url(),
                        'description': f'{old_registrante.name} perdió el dominio {dominio.full_domain()}'
                    }
                )

            if new_registrante:
                _create_registrant_event(
                    created_events, created_for_registrant, ct_registrante,
                    new_registrante, EVENT_REGISTERED,  # Got domain = like registered for them
                    {
                        'domain': dominio.full_domain(),
                        'url': new_registrante.get_absolute_url(),
                        'domain_url': dominio.get_absolute_url(),
                        'description': f'{new_registrante.name} obtuvo el dominio {dominio.full_domain()}'
                    }
                )

        elif campo == 'dominio_expire':
            # Renewal - notify current registrant
            if current_registrante and anterior and nuevo:
                if nuevo > anterior:
                    _create_registrant_event(
                        created_events, created_for_registrant, ct_registrante,
                        current_registrante, EVENT_RENEWED,
                        {
                            'domain': dominio.full_domain(),
                            'url': current_registrante.get_absolute_url(),
                            'domain_url': dominio.get_absolute_url(),
                            'description': f'{current_registrante.name} renovó el dominio {dominio.full_domain()}'
                        }
                    )
                else:
                    _create_registrant_event(
                        created_events, created_for_registrant, ct_registrante,
                        current_registrante, EVENT_RENEWED,
                        {
                            'domain': dominio.full_domain(),
                            'url': current_registrante.get_absolute_url(),
                            'domain_url': dominio.get_absolute_url(),
                            'description': (
                                f'{current_registrante.name} cambió la fecha de expiración '
                                f'para atrás (?) del dominio {dominio.full_domain()}'
                            )
                        }
                    )

        elif campo.startswith('DNS'):
            # DNS changed - notify current registrant (only once)
            if current_registrante:
                _create_registrant_event(
                    created_events, created_for_registrant, ct_registrante,
                    current_registrante, EVENT_DNS_CHANGED,
                    {
                        'domain': dominio.full_domain(),
                        'url': current_registrante.get_absolute_url(),
                        'domain_url': dominio.get_absolute_url(),
                        'description': f'El dominio {dominio.full_domain()} de {current_registrante.name} cambió DNS'
                    }
                )

    return created_events


def _create_registrant_event(
        created_events, created_for_registrant, ct_registrante,
        registrante, event_type, event_data
):
    """
    Helper to create a registrant event, avoiding duplicates.
    """
    if registrante.id not in created_for_registrant:
        created_for_registrant[registrante.id] = set()

    if event_type not in created_for_registrant[registrante.id]:
        event = Event.objects.create(
            event_type=event_type,
            content_type=ct_registrante,
            object_id=registrante.id,
            event_data=event_data
        )
        created_events.append(event)
        created_for_registrant[registrante.id].add(event_type)
        logger.info(f'Created registrant event {event_type} for {registrante.name}')


def get_related_registrantes_from_cambios(cambios):
    """
    Extract old and new registrante from a list of cambios.

    Args:
        cambios: List of change dicts

    Returns:
        Tuple of (old_registrante, new_registrante) - either can be None
    """
    from registrantes.models import Registrante

    old_registrante = None
    new_registrante = None

    for cambio in cambios:
        if cambio['campo'] == 'registrant_legal_uid':
            if cambio['anterior']:
                old_registrante = Registrante.objects.filter(legal_uid=cambio['anterior']).first()
            if cambio['nuevo']:
                new_registrante = Registrante.objects.filter(legal_uid=cambio['nuevo']).first()
            break

    return old_registrante, new_registrante
