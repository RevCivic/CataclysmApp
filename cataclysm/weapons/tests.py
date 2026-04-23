"""Smoke tests for weapons views."""
from django.test import TestCase
from django.urls import reverse

from .models import Weapon


class WeaponViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.weapon = Weapon.objects.create(
            name='Phaser',
            weapon_type='Energy',
            damage='2d6',
            critical='x2',
            range_increment=30,
            capacity=20,
            usage='2',
            special_properties='',
            weight='1.5',
            description='Standard issue phaser.',
        )

    def test_list_returns_200(self):
        resp = self.client.get(reverse('weapons:index'))
        self.assertEqual(resp.status_code, 200)

    def test_add_get_returns_200(self):
        resp = self.client.get(reverse('weapons:add'))
        self.assertEqual(resp.status_code, 200)

    def test_detail_returns_200(self):
        resp = self.client.get(reverse('weapons:detail', kwargs={'pk': self.weapon.pk}))
        self.assertEqual(resp.status_code, 200)

