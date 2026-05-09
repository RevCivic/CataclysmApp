"""Smoke tests for species views."""
from django.test import TestCase
from django.urls import reverse

from .models import Species


class SpeciesViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.species = Species.objects.create(
            species_name='Xelthari',
            home_world='Arrakis',
            size='Medium',
            type='Humanoid',
            air='Oxygen',
            sex='Binary',
            hours_of_sleep=8,
            days_without_food=14,
            days_without_water=3,
            strength=3,
            toughness=3,
            speed=3,
            intelligence=3,
            locomotion='Bipedal',
            status='Unknown',
            society='Unknown',
        )

    def test_index_returns_200(self):
        resp = self.client.get('/species/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Xelthari')

    def test_species_page_returns_200(self):
        resp = self.client.get(reverse('species_page', kwargs={'id': self.species.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Home World')
        self.assertContains(resp, 'Binary')

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('add'))
        self.assertEqual(resp.status_code, 200)

    def test_species_404_on_missing(self):
        resp = self.client.get(reverse('species_page', kwargs={'id': 9999}))
        self.assertEqual(resp.status_code, 404)
