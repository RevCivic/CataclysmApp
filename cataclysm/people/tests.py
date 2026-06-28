"""Smoke tests for people views."""
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

from .models import Person, Trait


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

    def test_add_person_get_returns_200(self):
        resp = self.client.get(reverse('add_person'))
        self.assertEqual(resp.status_code, 200)

    def test_edit_person_get_returns_200(self):
        resp = self.client.get(reverse('edit_person', kwargs={'id': self.person.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_person_404_on_missing(self):
        resp = self.client.get(reverse('person_page', kwargs={'id': 9999}))
        self.assertEqual(resp.status_code, 404)
