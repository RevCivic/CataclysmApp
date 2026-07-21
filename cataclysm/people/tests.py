"""Smoke tests for people views."""
import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

from .models import (
    AccommodationAssignment,
    Capability,
    OrganizationUnit,
    Person,
    PersonAlias,
    PersonAssignment,
    PersonCapability,
    PersonProfileFact,
    PersonRelationship,
    SavedPersonView,
    Trait,
)


class PeopleViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = Person.objects.create(
            name='Hugo Walgrave',
            age=42,
            sex='Male',
        )
        cls.trait = Trait.objects.create(name='Tactician')
        cls.tag = Tag.objects.create(name='Bridge Crew')
        cls.person.traits.add(cls.trait)
        cls.person.tags.add(cls.tag)

    def test_index_returns_200(self):
        resp = self.client.get('/people/')
        self.assertEqual(resp.status_code, 200)

    def test_index_contains_person(self):
        resp = self.client.get('/people/')
        self.assertContains(resp, 'Hugo Walgrave')

    def test_person_page_returns_200(self):
        resp = self.client.get(reverse('person_page', kwargs={'id': self.person.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_person_page_shows_trait(self):
        resp = self.client.get(reverse('person_page', kwargs={'id': self.person.pk}))
        self.assertContains(resp, 'Tactician')

    def test_person_page_shows_tag(self):
        resp = self.client.get(reverse('person_page', kwargs={'id': self.person.pk}))
        self.assertContains(resp, 'Bridge Crew')

    def test_index_filters_by_tag(self):
        other_person = Person.objects.create(name='Unaffiliated', age=30, sex='Female')
        other_tag = Tag.objects.create(name='Scientist')
        other_person.tags.add(other_tag)

        resp = self.client.get('/people/', {'tag': [self.tag.id]})

        self.assertContains(resp, 'Hugo Walgrave')
        self.assertNotContains(resp, 'Unaffiliated')

    def test_index_rejects_arbitrary_order_by_fields(self):
        resp = self.client.get('/people/', {'order_by': 'name; DROP TABLE people_person'})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['current_order_by'], 'name')

    def test_add_person_get_returns_200(self):
        resp = self.client.get(reverse('add_person'))
        self.assertEqual(resp.status_code, 200)

    def test_edit_person_get_returns_200(self):
        resp = self.client.get(reverse('edit_person', kwargs={'id': self.person.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_person_404_on_missing(self):
        resp = self.client.get(reverse('person_page', kwargs={'id': 9999}))
        self.assertEqual(resp.status_code, 404)


class ImportedPeopleModelTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(name='Unknown-age crew', age_text='>100')

    def test_person_preserves_non_numeric_age(self):
        self.assertIsNone(self.person.age)
        self.assertEqual(self.person.age_text, '>100')

    def test_alias_and_capability_names_are_normalized(self):
        alias = PersonAlias.objects.create(person=self.person, name='  The   Whisper  ')
        capability = Capability.objects.create(name='  Martial   Artist ', category='Combat')
        PersonCapability.objects.create(person=self.person, capability=capability, raw_marker='X')

        self.assertEqual(alias.normalized_name, 'the whisper')
        self.assertEqual(capability.normalized_name, 'martial artist')
        self.assertEqual(self.person.capabilities.get().raw_marker, 'X')

    def test_character_facts_can_be_bound(self):
        ship = OrganizationUnit.objects.create(name='Potempkin', kind=OrganizationUnit.Kind.SHIP)
        assignment = PersonAssignment.objects.create(
            person=self.person,
            unit=ship,
            role='Engineer',
            rank='LT',
            status='Good',
        )
        accommodation = AccommodationAssignment.objects.create(
            person=self.person,
            room='319',
            section='B',
            direction='Starboard',
            room_type='Single',
        )
        fact = PersonProfileFact.objects.create(
            person=self.person,
            key='origin',
            value='Mountain Base',
            normalized_value='mountain base',
        )
        relationship = PersonRelationship.objects.create(
            from_person=self.person,
            unresolved_name='Unmatched Parent',
            relationship_type='child of',
        )

        self.assertEqual(assignment.unit, ship)
        self.assertEqual(accommodation.section, 'B')
        self.assertEqual(fact.value, 'Mountain Base')
        self.assertEqual(relationship.unresolved_name, 'Unmatched Parent')


class PeopleDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.engineer = Person.objects.create(name='Engineer One', age=30)
        cls.hidden = Person.objects.create(name='Hidden Engineer', age=31, hidden=True)
        cls.pilot = Person.objects.create(name='Pilot Two', age=32)
        cls.engineer.aliases.create(name='The Fixer')
        ship = OrganizationUnit.objects.create(name='Potempkin', kind=OrganizationUnit.Kind.SHIP)
        PersonAssignment.objects.create(
            person=cls.engineer,
            unit=ship,
            role='Engineer',
            rank='LT',
            status='Good',
        )
        engineering = Capability.objects.create(name='Engineering')
        command = Capability.objects.create(name='Command')
        PersonCapability.objects.create(person=cls.engineer, capability=engineering)
        PersonCapability.objects.create(person=cls.engineer, capability=command)
        PersonCapability.objects.create(person=cls.pilot, capability=command)
        cls.engineering_id = engineering.id
        cls.command_id = command.id
        cls.ship_id = ship.id

    def test_search_matches_alias_and_hides_hidden_people(self):
        response = self.client.get('/people/', {'q': 'Fixer'})

        self.assertContains(response, 'Engineer One')
        self.assertNotContains(response, 'Hidden Engineer')

    def test_capability_filters_use_and_semantics(self):
        response = self.client.get(
            '/people/',
            {'capability': [self.engineering_id, self.command_id]},
        )

        self.assertContains(response, 'Engineer One')
        self.assertNotContains(response, 'Pilot Two')

    def test_assignment_filters_can_be_combined(self):
        response = self.client.get(
            '/people/',
            {'unit': self.ship_id, 'status': 'Good', 'role': 'engineer', 'rank': 'lt'},
        )

        self.assertContains(response, 'Engineer One')
        self.assertNotContains(response, 'Pilot Two')


class SavedPeopleViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(username='view-owner', password='secret-pass')
        cls.other = get_user_model().objects.create_user(username='other-user', password='secret-pass')
        Person.objects.create(name='Engineer Export', age=30, position='Engineer')
        Person.objects.create(name='Pilot Export', age=31, position='Pilot')

    def test_authenticated_user_can_save_and_open_validated_view(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('save_person_view'),
            {'name': 'Engineers', 'visibility': 'private', 'query_string': 'role=Engineer&order_by=not-a-field'},
        )

        saved_view = SavedPersonView.objects.get(owner=self.owner)
        self.assertEqual(saved_view.filters['role'], 'Engineer')
        self.assertEqual(saved_view.filters['order_by'], 'name')
        self.assertIn('assignments', saved_view.columns)
        self.assertRedirects(response, '/people/?role=Engineer&order_by=name')
        opened = self.client.get(reverse('open_person_view', kwargs={'view_id': saved_view.id}))
        self.assertRedirects(opened, '/people/?role=Engineer&order_by=name')

    def test_private_view_is_not_visible_to_another_user(self):
        saved_view = SavedPersonView.objects.create(
            owner=self.owner,
            name='Private',
            filters={'role': 'Engineer'},
        )
        self.client.force_login(self.other)

        response = self.client.get(reverse('open_person_view', kwargs={'view_id': saved_view.id}))

        self.assertEqual(response.status_code, 404)

    def test_shared_view_can_be_opened_anonymously(self):
        saved_view = SavedPersonView.objects.create(
            owner=self.owner,
            name='Shared',
            visibility=SavedPersonView.Visibility.SHARED,
            filters={'role': 'Pilot'},
        )

        response = self.client.get(reverse('open_person_view', kwargs={'view_id': saved_view.id}))

        self.assertRedirects(response, '/people/?role=Pilot&order_by=name')

    def test_csv_export_uses_current_filters(self):
        response = self.client.get(
            reverse('export_people_csv'),
            {'role': 'Engineer', 'column': ['name', 'position']},
        )
        rows = list(csv.reader(io.StringIO(response.content.decode())))

        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(rows[0], ['Name', 'Position'])
        self.assertEqual(rows[1][0], 'Engineer Export')
        self.assertEqual(len(rows), 2)

    def test_csv_export_escapes_spreadsheet_formulas(self):
        Person.objects.create(name='=HYPERLINK("bad")', age=20)

        response = self.client.get(reverse('export_people_csv'), {'q': 'HYPERLINK', 'column': 'name'})
        rows = list(csv.reader(io.StringIO(response.content.decode())))

        self.assertEqual(rows[1][0], "'=HYPERLINK(\"bad\")")

    def test_saved_view_restores_selected_columns(self):
        saved_view = SavedPersonView.objects.create(
            owner=self.owner,
            name='Compact',
            visibility=SavedPersonView.Visibility.SHARED,
            filters={'role': 'Engineer'},
            columns=['name', 'assignments'],
        )

        response = self.client.get(reverse('open_person_view', kwargs={'view_id': saved_view.id}))

        self.assertRedirects(
            response,
            '/people/?role=Engineer&order_by=name&column=name&column=assignments',
        )
