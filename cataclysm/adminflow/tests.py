from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from species.models import Species


class AdminflowViewsTestCase(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='adminflow-user', password='pass12345')
        self.client.force_login(self.user)

    def test_admin_index_shows_submenus(self):
        response = self.client.get(reverse('adminflow:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Open People Tools')
        self.assertContains(response, 'Open Species Tools')

    def test_species_upload_preview_shows_mapping_step(self):
        upload = SimpleUploadedFile(
            'species.csv',
            b'Species_Name,Home_World,Strength\nAvians,Skye,4\n',
            content_type='text/csv',
        )
        response = self.client.post(reverse('adminflow:species_upload'), {'csv_file': upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Match Fields')
        self.assertContains(response, 'Species Name *')

    def test_species_import_creates_species_from_mapped_csv(self):
        upload = SimpleUploadedFile(
            'species.csv',
            (
                b'Species_Name,Home_World,Strength,Natural_Weapon,Light_Grav,Attributes,Special_Abilities\n'
                b'Avians,Skye,4,yes,yes,Swift;Graceful,Glide;Sonic Cry\n'
            ),
            content_type='text/csv',
        )
        self.client.post(reverse('adminflow:species_upload'), {'csv_file': upload})

        response = self.client.post(
            reverse('adminflow:species_import'),
            {
                'species_name': 'Species_Name',
                'home_world': 'Home_World',
                'strength': 'Strength',
                'natural_weapon': 'Natural_Weapon',
                'light_grav': 'Light_Grav',
                'attributes': 'Attributes',
                'special_abilities': 'Special_Abilities',
            },
        )

        self.assertEqual(response.status_code, 200)
        species = Species.objects.get(species_name='Avians')
        self.assertEqual(species.home_world, 'Skye')
        self.assertEqual(species.strength, 4)
        self.assertTrue(species.natural_weapon)
        self.assertTrue(species.light_grav)
        self.assertEqual(species.attributes, ['Swift', 'Graceful'])
        self.assertEqual(species.special_abilities, ['Glide', 'Sonic Cry'])
        self.assertContains(response, 'created 1')
