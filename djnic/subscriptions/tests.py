from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from dominios.models import Dominio, STATUS_DISPONIBLE, STATUS_NO_DISPONIBLE
from zonas.models import Zona
from registrantes.models import Registrante
from subscriptions.models import (
    Event, EVENT_DROPPED, EVENT_REGISTERED, EVENT_RENEWED,
    EVENT_REGISTRANT_CHANGED, EVENT_DNS_CHANGED
)
from subscriptions.events import (
    register_events,
    get_related_registrantes_from_cambios
)


class EventCreationTestCase(TestCase):
    """Tests for the event creation system."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante1 = Registrante.objects.create(
            name='Empresa Uno SA',
            legal_uid='30-12345678-9',
            created=timezone.now(),
            changed=timezone.now()
        )
        cls.registrante2 = Registrante.objects.create(
            name='Empresa Dos SRL',
            legal_uid='30-98765432-1',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        # Clear events before each test
        Event.objects.all().delete()
        # Create a fresh domain for each test
        self.dominio = Dominio.objects.create(
            nombre='testdomain',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante1,
            expire=timezone.now()
        )

    def test_no_events_for_empty_cambios(self):
        """No events should be created when cambios is empty."""
        events = register_events(self.dominio, [])
        self.assertEqual(len(events), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_no_events_for_none_cambios(self):
        """No events should be created when cambios is None."""
        events = register_events(self.dominio, None)
        self.assertEqual(len(events), 0)


class DomainDroppedEventTestCase(TestCase):
    """Tests for EVENT_DROPPED creation."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Empresa Test',
            legal_uid='30-11111111-1',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='dropping',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_domain_dropped_event_created(self):
        """EVENT_DROPPED should be created when domain status changes from 'no disponible' to 'disponible'."""
        cambios = [{"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"}]

        events = register_events(self.dominio, cambios)

        # Should create 2 events: one for domain, one for registrant
        self.assertEqual(len(events), 2)

        # Check domain event
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_DROPPED)
        self.assertEqual(domain_events[0].object_id, self.dominio.id)
        self.assertIn('domain', domain_events[0].event_data)
        self.assertIn('url', domain_events[0].event_data)

    def test_domain_dropped_registrant_event_created(self):
        """EVENT_DROPPED should also create an event for the registrant who lost the domain."""
        cambios = [{"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"}]

        events = register_events(self.dominio, cambios)

        # Check registrant event
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 1)
        self.assertEqual(registrant_events[0].event_type, EVENT_DROPPED)
        self.assertEqual(registrant_events[0].object_id, self.registrante.id)
        self.assertIn('domain', registrant_events[0].event_data)
        self.assertIn('domain_url', registrant_events[0].event_data)


class DomainRegisteredEventTestCase(TestCase):
    """Tests for EVENT_REGISTERED creation."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Nueva Empresa',
            legal_uid='30-22222222-2',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='newdomain',
            zona=self.zona,
            estado=STATUS_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_domain_registered_event_created(self):
        """EVENT_REGISTERED should be created when domain status changes from 'disponible' to 'no disponible'."""
        cambios = [{"campo": "estado", "anterior": "disponible", "nuevo": "no disponible"}]

        events = register_events(self.dominio, cambios)

        # Should create 2 events: one for domain, one for registrant
        self.assertEqual(len(events), 2)

        # Check domain event
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_REGISTERED)

    def test_domain_registered_registrant_event_created(self):
        """EVENT_REGISTERED should also create an event for the registrant who got the domain."""
        cambios = [{"campo": "estado", "anterior": "disponible", "nuevo": "no disponible"}]

        events = register_events(self.dominio, cambios)

        # Check registrant event
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 1)
        self.assertEqual(registrant_events[0].event_type, EVENT_REGISTERED)


class DomainRenewedEventTestCase(TestCase):
    """Tests for EVENT_RENEWED creation."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Empresa Renovadora',
            legal_uid='30-33333333-3',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='renewed',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_domain_renewed_event_created(self):
        """EVENT_RENEWED should be created when expire date is extended."""
        cambios = [{
            "campo": "dominio_expire",
            "anterior": "2024-01-01 00:00:00",
            "nuevo": "2025-01-01 00:00:00"
        }]

        events = register_events(self.dominio, cambios)

        # Should create 2 events: one for domain, one for registrant
        self.assertEqual(len(events), 2)

        # Check domain event
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_RENEWED)
        self.assertIn('renovado', domain_events[0].event_data['description'])

    def test_domain_renewed_registrant_event_created(self):
        """EVENT_RENEWED should also create an event for the current registrant."""
        cambios = [{
            "campo": "dominio_expire",
            "anterior": "2024-01-01 00:00:00",
            "nuevo": "2025-01-01 00:00:00"
        }]

        events = register_events(self.dominio, cambios)

        # Check registrant event
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 1)
        self.assertEqual(registrant_events[0].event_type, EVENT_RENEWED)

    def test_renewed_event_for_date_going_back(self):
        """EVENT_RENEWED is created for registrant even when expire date goes backwards (edge case)."""
        cambios = [{
            "campo": "dominio_expire",
            "anterior": "2025-01-01 00:00:00",
            "nuevo": "2024-01-01 00:00:00"
        }]

        events = register_events(self.dominio, cambios)

        # Domain gets an event (with different description for backward change)
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertIn('para atras', domain_events[0].event_data['description'])

        # Registrant also gets an event with special description
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 1)
        self.assertIn('para atrás', registrant_events[0].event_data['description'])


class RegistrantChangedEventTestCase(TestCase):
    """Tests for EVENT_REGISTRANT_CHANGED creation."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.old_registrante = Registrante.objects.create(
            name='Antiguo Dueño',
            legal_uid='30-44444444-4',
            created=timezone.now(),
            changed=timezone.now()
        )
        cls.new_registrante = Registrante.objects.create(
            name='Nuevo Dueño',
            legal_uid='30-55555555-5',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='transferred',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.new_registrante,
            expire=timezone.now()
        )

    def test_registrant_changed_domain_event(self):
        """EVENT_REGISTRANT_CHANGED should be created for the domain."""
        cambios = [{
            "campo": "registrant_legal_uid",
            "anterior": self.old_registrante.legal_uid,
            "nuevo": self.new_registrante.legal_uid
        }]

        events = register_events(self.dominio, cambios)

        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_REGISTRANT_CHANGED)
        self.assertIn('old_registrante_name', domain_events[0].event_data)
        self.assertIn('new_registrante_name', domain_events[0].event_data)

    def test_registrant_changed_creates_events_for_both_registrants(self):
        """Registrant change should create events for BOTH old and new registrants."""
        cambios = [{
            "campo": "registrant_legal_uid",
            "anterior": self.old_registrante.legal_uid,
            "nuevo": self.new_registrante.legal_uid
        }]

        events = register_events(self.dominio, cambios)

        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 2)

        # Old registrant gets DROPPED event (lost the domain)
        old_reg_event = [e for e in registrant_events if e.object_id == self.old_registrante.id][0]
        self.assertEqual(old_reg_event.event_type, EVENT_DROPPED)
        self.assertIn('perdió', old_reg_event.event_data['description'])

        # New registrant gets REGISTERED event (got the domain)
        new_reg_event = [e for e in registrant_events if e.object_id == self.new_registrante.id][0]
        self.assertEqual(new_reg_event.event_type, EVENT_REGISTERED)
        self.assertIn('obtuvo', new_reg_event.event_data['description'])


class DNSChangedEventTestCase(TestCase):
    """Tests for EVENT_DNS_CHANGED creation."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='DNS Changer',
            legal_uid='30-66666666-6',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='dnschange',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_dns_changed_event_created(self):
        """EVENT_DNS_CHANGED should be created when DNS changes."""
        cambios = [{"campo": "DNS1", "anterior": "ns1.old.com", "nuevo": "ns1.new.com"}]

        events = register_events(self.dominio, cambios)

        self.assertEqual(len(events), 2)  # Domain + registrant

        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_DNS_CHANGED)

    def test_multiple_dns_changes_create_single_event(self):
        """Multiple DNS changes should only create ONE DNS_CHANGED event per entity."""
        cambios = [
            {"campo": "DNS1", "anterior": "ns1.old.com", "nuevo": "ns1.new.com"},
            {"campo": "DNS2", "anterior": "ns2.old.com", "nuevo": "ns2.new.com"},
            {"campo": "DNS3", "anterior": "", "nuevo": "ns3.new.com"},
        ]

        events = register_events(self.dominio, cambios)

        # Only 2 events: one DNS_CHANGED for domain, one for registrant
        self.assertEqual(len(events), 2)

        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 1)
        self.assertEqual(domain_events[0].event_type, EVENT_DNS_CHANGED)


class MultipleChangesEventTestCase(TestCase):
    """Tests for multiple simultaneous changes."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Multi Changer',
            legal_uid='30-77777777-7',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='multichange',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_multiple_different_changes(self):
        """Multiple different types of changes should each create their own events."""
        cambios = [
            {"campo": "dominio_expire", "anterior": "2024-01-01 00:00:00", "nuevo": "2025-01-01 00:00:00"},
            {"campo": "DNS1", "anterior": "ns1.old.com", "nuevo": "ns1.new.com"},
        ]

        events = register_events(self.dominio, cambios)

        # Domain events: RENEWED + DNS_CHANGED = 2
        # Registrant events: RENEWED + DNS_CHANGED = 2
        # Total = 4
        self.assertEqual(len(events), 4)

        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        domain_event_types = {e.event_type for e in domain_events}
        self.assertIn(EVENT_RENEWED, domain_event_types)
        self.assertIn(EVENT_DNS_CHANGED, domain_event_types)


class GetRelatedRegistrantesTestCase(TestCase):
    """Tests for get_related_registrantes_from_cambios helper."""

    @classmethod
    def setUpTestData(cls):
        cls.registrante1 = Registrante.objects.create(
            name='First Owner',
            legal_uid='30-88888888-8',
            created=timezone.now(),
            changed=timezone.now()
        )
        cls.registrante2 = Registrante.objects.create(
            name='Second Owner',
            legal_uid='30-99999999-9',
            created=timezone.now(),
            changed=timezone.now()
        )

    def test_extracts_both_registrants(self):
        """Should extract both old and new registrants from cambios."""
        cambios = [{
            "campo": "registrant_legal_uid",
            "anterior": self.registrante1.legal_uid,
            "nuevo": self.registrante2.legal_uid
        }]

        old_reg, new_reg = get_related_registrantes_from_cambios(cambios)

        self.assertEqual(old_reg, self.registrante1)
        self.assertEqual(new_reg, self.registrante2)

    def test_handles_missing_old_registrant(self):
        """Should handle case where old registrant doesn't exist."""
        cambios = [{
            "campo": "registrant_legal_uid",
            "anterior": "30-00000000-0",  # Non-existent
            "nuevo": self.registrante2.legal_uid
        }]

        old_reg, new_reg = get_related_registrantes_from_cambios(cambios)

        self.assertIsNone(old_reg)
        self.assertEqual(new_reg, self.registrante2)

    def test_handles_no_registrant_change(self):
        """Should return None for both when no registrant change in cambios."""
        cambios = [{"campo": "DNS1", "anterior": "old.dns", "nuevo": "new.dns"}]

        old_reg, new_reg = get_related_registrantes_from_cambios(cambios)

        self.assertIsNone(old_reg)
        self.assertIsNone(new_reg)


class EventDataContentsTestCase(TestCase):
    """Tests to verify event_data contains required fields."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Data Checker',
            legal_uid='30-10101010-1',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='datacheck',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_domain_event_contains_url(self):
        """Domain events should contain 'url' in event_data."""
        cambios = [{"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"}]

        events = register_events(self.dominio, cambios)

        domain_event = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)][0]
        self.assertIn('url', domain_event.event_data)
        self.assertIn('domain', domain_event.event_data)
        self.assertIn('description', domain_event.event_data)

    def test_registrant_event_contains_domain_url(self):
        """Registrant events should contain 'domain_url' in event_data."""
        cambios = [{"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"}]

        events = register_events(self.dominio, cambios)

        registrant_event = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)][0]
        self.assertIn('domain_url', registrant_event.event_data)
        self.assertIn('domain', registrant_event.event_data)
        self.assertIn('url', registrant_event.event_data)  # Link to registrant


class NewDomainRegistrationEventTestCase(TestCase):
    """Tests for events when a NEW domain is added to the database (just_created=True)."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='New Domain Owner',
            legal_uid='30-13131313-1',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        # This simulates a domain that was just added to our database
        self.dominio = Dominio.objects.create(
            nombre='brandnew',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_new_domain_creates_registered_event(self):
        """When a new domain is added to our database, EVENT_REGISTERED should be created."""
        # This is the cambios structure used in update_from_wa_object for just_created=True
        cambios = [
            {"campo": "estado", "anterior": STATUS_DISPONIBLE, "nuevo": STATUS_NO_DISPONIBLE},
            {"campo": "registrant_legal_uid", "anterior": "", "nuevo": self.registrante.legal_uid},
            {"campo": "registrant_name", "anterior": "", "nuevo": self.registrante.name},
        ]

        events = register_events(self.dominio, cambios)

        # Should have domain REGISTERED event
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        registered_events = [e for e in domain_events if e.event_type == EVENT_REGISTERED]
        self.assertEqual(len(registered_events), 1)

    def test_new_domain_creates_registrant_event(self):
        """New domain should also create EVENT_REGISTERED for the registrant."""
        cambios = [
            {"campo": "estado", "anterior": STATUS_DISPONIBLE, "nuevo": STATUS_NO_DISPONIBLE},
            {"campo": "registrant_legal_uid", "anterior": "", "nuevo": self.registrante.legal_uid},
        ]

        events = register_events(self.dominio, cambios)

        # Should have registrant REGISTERED event
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        # Two REGISTERED events: one from estado change, one from registrant_legal_uid change
        registered_events = [e for e in registrant_events if e.event_type == EVENT_REGISTERED]
        self.assertGreaterEqual(len(registered_events), 1)

    def test_new_domain_with_no_registrant(self):
        """New domain without registrant (free domain case) should still work."""
        self.dominio.registrante = None
        self.dominio.save()

        cambios = [
            {"campo": "estado", "anterior": STATUS_DISPONIBLE, "nuevo": STATUS_NO_DISPONIBLE},
            {"campo": "registrant_legal_uid", "anterior": "", "nuevo": ""},
        ]

        events = register_events(self.dominio, cambios)

        # Should have domain events: REGISTERED + REGISTRANT_CHANGED
        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        self.assertEqual(len(domain_events), 2)
        domain_event_types = {e.event_type for e in domain_events}
        self.assertIn(EVENT_REGISTERED, domain_event_types)
        self.assertIn(EVENT_REGISTRANT_CHANGED, domain_event_types)

        # No registrant events since there's no registrant
        registrant_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Registrante)]
        self.assertEqual(len(registrant_events), 0)


class NoDuplicateEventsTestCase(TestCase):
    """Tests to ensure no duplicate events are created."""

    @classmethod
    def setUpTestData(cls):
        cls.zona = Zona.objects.create(nombre='com.ar', tz='America/Argentina/Buenos_Aires')
        cls.registrante = Registrante.objects.create(
            name='Duplicate Avoider',
            legal_uid='30-12121212-1',
            created=timezone.now(),
            changed=timezone.now()
        )

    def setUp(self):
        Event.objects.all().delete()
        self.dominio = Dominio.objects.create(
            nombre='nodups',
            zona=self.zona,
            estado=STATUS_NO_DISPONIBLE,
            registrante=self.registrante,
            expire=timezone.now()
        )

    def test_no_duplicate_event_types_for_domain(self):
        """Same event type should not be created twice for the same domain."""
        # Even if we have weird duplicate cambios (shouldn't happen but let's be safe)
        cambios = [
            {"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"},
            {"campo": "estado", "anterior": "no disponible", "nuevo": "disponible"},  # Duplicate
        ]

        events = register_events(self.dominio, cambios)

        domain_events = [e for e in events if e.content_type == ContentType.objects.get_for_model(Dominio)]
        # Should only have 1 DROPPED event, not 2
        dropped_events = [e for e in domain_events if e.event_type == EVENT_DROPPED]
        self.assertEqual(len(dropped_events), 1)
