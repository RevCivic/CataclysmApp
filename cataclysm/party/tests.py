"""Smoke tests for party views."""
from django.test import TestCase
from django.urls import reverse

from .models import Party


class PartyViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.party = Party.objects.create(
            name='The Family',
            type='Crew',
            leader='Hugo Walgrave',
            purpose='Explore and remap the stars.',
        )

    def test_list_returns_200(self):
        resp = self.client.get(reverse('party_index'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        resp = self.client.get(reverse('party_page', kwargs={'pk': self.party.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('add_party'))
        self.assertEqual(resp.status_code, 200)

    def test_edit_get_returns_200(self):
        resp = self.client.get(reverse('edit_party', kwargs={'pk': self.party.pk}))
        self.assertEqual(resp.status_code, 200)

