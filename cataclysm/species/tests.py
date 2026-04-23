"""Smoke tests for species views."""
from django.test import TestCase
from django.urls import reverse

from .models import Species


class SpeciesViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.species = Species.objects.create(
            name='Xelthari',
            home_world='Arrakis',
            size='medium',
            type='animal',
            air='oxygen',
            reproduction_method='standard',
            hours_of_sleep=8,
            days_without_food=14,
            days_without_water=3,
            strength_rating=3,
            toughness_rating=3,
            speed_rating=3,
            intelligence_rating=3,
            gravity='standard',
            locomotion_method='bipedal',
            accord_status='unknown',
            society='unknown',
        )

    def test_index_returns_200(self):
        resp = self.client.get('/species/')
        self.assertEqual(resp.status_code, 200)

    def test_species_page_returns_200(self):
        resp = self.client.get(reverse('species_page', kwargs={'id': self.species.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('add'))
        self.assertEqual(resp.status_code, 200)

    def test_species_404_on_missing(self):
        resp = self.client.get(reverse('species_page', kwargs={'id': 9999}))
        self.assertEqual(resp.status_code, 404)

