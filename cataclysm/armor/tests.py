"""Smoke tests for armor views."""
from django.test import TestCase
from django.urls import reverse

from tags.models import Tag

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

    def test_list_filters_by_tag(self):
        tagged_armor = Armor.objects.create(
            name='Tagged Armor',
            armor_type='Light',
            base_armor_class=2,
            max_dexterity_bonus=6,
            armor_check_penalty=0,
            speed_penalty=0,
            weight='1.0',
            description='Tagged',
        )
        other_armor = Armor.objects.create(
            name='Other Armor',
            armor_type='Heavy',
            base_armor_class=4,
            max_dexterity_bonus=2,
            armor_check_penalty=-2,
            speed_penalty=-5,
            weight='4.0',
            description='Other',
        )
        tag = Tag.objects.create(name='Tactical')
        other_tag = Tag.objects.create(name='Ceremonial')
        tagged_armor.tags.add(tag)
        other_armor.tags.add(other_tag)

        resp = self.client.get(reverse('armor:index'), {'tag': [tag.id]})

        self.assertContains(resp, 'Tagged Armor')
        self.assertNotContains(resp, 'Other Armor')
