"""Smoke tests for factions views."""
from django.test import TestCase
from django.urls import reverse

from .models import Faction


class FactionViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faction = Faction.objects.create(
            name='Galactic Accord',
            description='A peaceful federation of worlds.',
        )

    def test_list_returns_200(self):
        resp = self.client.get(reverse('factions:index'))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('factions:add'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        resp = self.client.get(reverse('factions:detail', kwargs={'pk': self.faction.pk}))
        self.assertEqual(resp.status_code, 200)

