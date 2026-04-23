"""Smoke tests for events views."""
from django.test import TestCase
from django.urls import reverse

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

