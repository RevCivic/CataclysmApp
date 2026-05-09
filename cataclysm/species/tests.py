"""Tests for species views and import helpers."""
import importlib

from django.test import TestCase
from django.urls import reverse

from .importing import guess_field_mapping
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


class SpeciesImportHelpersTestCase(TestCase):
    def test_guess_field_mapping_matches_alias_headers(self):
        mapping = guess_field_mapping(['name', 'can_fly', 'strength_rating', 'Special Abilities'])
        self.assertEqual(mapping['species_name'], 'name')
        self.assertEqual(mapping['flier'], 'can_fly')
        self.assertEqual(mapping['strength'], 'strength_rating')
        self.assertEqual(mapping['special_abilities'], 'Special Abilities')

    def test_migrate_gravity_flags_sets_boolean_fields(self):
        migration_module = importlib.import_module('species.migrations.0008_species_schema_refresh')

        class FakeSpeciesRecord:
            def __init__(self, gravity):
                self.gravity = gravity
                self.light_grav = False
                self.heavy_grav = False

        class FakeManager:
            def __init__(self, records):
                self.records = records
                self.bulk_updates = []

            def iterator(self, chunk_size=None):
                return iter(self.records)

            def bulk_update(self, records, fields):
                self.bulk_updates.append((list(records), list(fields)))

        records = [
            FakeSpeciesRecord('light'),
            FakeSpeciesRecord('heavy'),
            FakeSpeciesRecord('standard'),
        ]
        manager = FakeManager(records)
        fake_species_model = type('FakeSpeciesModel', (), {'objects': manager})
        fake_apps = type('FakeApps', (), {'get_model': staticmethod(lambda app_label, model_name: fake_species_model)})

        migration_module.migrate_gravity_flags(fake_apps, None)

        self.assertTrue(records[0].light_grav)
        self.assertFalse(records[0].heavy_grav)
        self.assertFalse(records[1].light_grav)
        self.assertTrue(records[1].heavy_grav)
        self.assertFalse(records[2].light_grav)
        self.assertFalse(records[2].heavy_grav)
        self.assertEqual(manager.bulk_updates[0][1], ['light_grav', 'heavy_grav'])
