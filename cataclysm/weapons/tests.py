"""Smoke tests for weapons views."""
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

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

    def test_list_filters_by_tag(self):
        other_weapon = Weapon.objects.create(
            name='Rifle',
            weapon_type='Ballistic',
            damage='1d10',
            critical='x2',
            range_increment=60,
            capacity=5,
            usage='1',
            special_properties='',
            weight='3.0',
            description='Long-range rifle.',
        )
        tag = Tag.objects.create(name='Sidearm')
        other_tag = Tag.objects.create(name='Long Range')
        self.weapon.tags.add(tag)
        other_weapon.tags.add(other_tag)

        resp = self.client.get(reverse('weapons:index'), {'tag': [tag.id]})

        self.assertContains(resp, 'Phaser')
        self.assertNotContains(resp, 'Rifle')
