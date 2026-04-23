"""Smoke tests for armor views."""
from django.test import TestCase
from django.urls import reverse

from .models import Armor


class ArmorViewsTestCase(TestCase):
    def test_list_returns_200(self):
        resp = self.client.get(reverse('armor:index'))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('armor:add'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        armor = Armor.objects.create(
            name='Test Armor',
            armor_type='Light',
            base_armor_class=2,
            max_dexterity_bonus=6,
            armor_check_penalty=0,
            speed_penalty=0,
            weight='1.0',
            description='Test',
        )
        resp = self.client.get(reverse('armor:detail', kwargs={'pk': armor.pk}))
        self.assertEqual(resp.status_code, 200)

