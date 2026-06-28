"""Smoke tests for worlds views."""
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

from .models import World


class WorldViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.world = World.objects.create(
            name='Arrakis',
            system='Canopus',
            planet_class='D',
            moons=2,
            colonized=True,
            terraformed=False,
            contains_flora=False,
            contains_fauna=True,
            contains_sentient_life=True,
            special_traits=[],
            points_of_interest=[],
        )

    def test_list_returns_200(self):
        resp = self.client.get(reverse('worlds:index'))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('worlds:add'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        resp = self.client.get(reverse('worlds:detail', kwargs={'pk': self.world.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_list_filters_by_tag(self):
        other_world = World.objects.create(
            name='Borealis',
            system='Trappist',
            planet_class='M',
            moons=1,
            colonized=False,
            terraformed=False,
            contains_flora=True,
            contains_fauna=False,
            contains_sentient_life=False,
            special_traits=[],
            points_of_interest=[],
        )
        tag = Tag.objects.create(name='Core')
        other_tag = Tag.objects.create(name='Frontier')
        self.world.tags.add(tag)
        other_world.tags.add(other_tag)

        resp = self.client.get(reverse('worlds:index'), {'tag': [tag.id]})

        self.assertContains(resp, 'Arrakis')
        self.assertNotContains(resp, 'Borealis')
