"""Smoke tests for events views."""
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

from .models import Event


class EventViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(
            name='First Contact',
            description='The first contact event.',
            location='Deep Space',
            event_type='event',
        )

    def test_list_returns_200(self):
        resp = self.client.get(reverse('events:index'))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('events:add'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        resp = self.client.get(reverse('events:detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_list_filters_by_tag(self):
        other_event = Event.objects.create(
            name='Unrelated Event',
            description='Another event.',
            location='Unknown',
            event_type='event',
        )
        tag = Tag.objects.create(name='Historic')
        other_tag = Tag.objects.create(name='Secret')
        self.event.tags.add(tag)
        other_event.tags.add(other_tag)

        resp = self.client.get(reverse('events:index'), {'tag': [tag.id]})

        self.assertContains(resp, 'First Contact')
        self.assertNotContains(resp, 'Unrelated Event')
