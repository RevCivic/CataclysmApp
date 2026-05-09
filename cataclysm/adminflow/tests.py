from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from adminflow.views import _decode_csv_file
from people.models import Person
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
        self.assertContains(response, 'Download Images from Sheet')

    def test_run_download_images_from_general_admin_tasks(self):
        def fake_call_command(*args, **kwargs):
            kwargs['stdout'].write('Processed rows=1')

        with patch('adminflow.views.call_command', side_effect=fake_call_command) as mock_call:
            response = self.client.post(
                reverse('adminflow:run_download_images'),
                {
                    'spreadsheet_id': 'dummy-sheet-id',
                    'dry_run': 'on',
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Processed rows=1')
        args, kwargs = mock_call.call_args
        self.assertEqual(args[0], 'download_sheet_images')
        self.assertEqual(kwargs['spreadsheet_id'], 'dummy-sheet-id')
        self.assertTrue(kwargs['dry_run'])
        self.assertFalse(kwargs['overwrite'])

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

    def test_decode_csv_file_supports_utf8_bom_and_latin1(self):
        utf8_bom_upload = SimpleUploadedFile('species.csv', 'Species_Name\nAvians\n'.encode('utf-8-sig'))
        latin1_upload = SimpleUploadedFile('species.csv', 'Species_Name\nCaf\xe9\n'.encode('latin-1'))

        self.assertIn('Avians', _decode_csv_file(utf8_bom_upload))
        self.assertIn('Caf\xe9', _decode_csv_file(latin1_upload))

    def test_people_species_upload_updates_person_species_by_name(self):
        old_species = Species.objects.create(species_name='Human')
        new_species = Species.objects.create(species_name='Ketraken')
        person = Person.objects.create(name='Talabevel Banrahal', age=30, species=old_species)

        upload = SimpleUploadedFile(
            'people_species.csv',
            b'name,species\nTalabevel Banrahal,Ketraken\n',
            content_type='text/csv',
        )

        response = self.client.post(reverse('adminflow:people_species_upload'), {'csv_file': upload})
        self.assertEqual(response.status_code, 200)

        person.refresh_from_db()
        self.assertEqual(person.species, new_species)
        self.assertContains(response, 'updated 1, unchanged 0, skipped 0')

    def test_people_species_upload_requires_name_and_species_columns(self):
        upload = SimpleUploadedFile(
            'people_species.csv',
            b'person_name,species_name\nTalabevel Banrahal,Ketraken\n',
            content_type='text/csv',
        )

        response = self.client.post(reverse('adminflow:people_species_upload'), {'csv_file': upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CSV must include both &quot;name&quot; and &quot;species&quot; columns.')

    def test_people_species_upload_matches_case_insensitively(self):
        old_species = Species.objects.create(species_name='Human')
        new_species = Species.objects.create(species_name='Ketraken')
        person = Person.objects.create(name='Talabevel Banrahal', age=30, species=old_species)

        upload = SimpleUploadedFile(
            'people_species.csv',
            b'name,species\nTALABEVEL BANRAHAL,ketraken\n',
            content_type='text/csv',
        )

        response = self.client.post(reverse('adminflow:people_species_upload'), {'csv_file': upload})
        self.assertEqual(response.status_code, 200)

        person.refresh_from_db()
        self.assertEqual(person.species, new_species)
        self.assertContains(response, 'updated 1, unchanged 0, skipped 0')
