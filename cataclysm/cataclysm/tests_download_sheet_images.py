"""Tests for the download_sheet_images management command."""
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from people.models import Person
from species.models import Species

from .management.commands.download_sheet_images import _row_url_pair, _url_from_cell


class DownloadSheetImagesHelpersTestCase(TestCase):
    def test_url_from_cell_extracts_plain_and_formula_links(self):
        self.assertEqual(_url_from_cell("https://example.com/a.png"), "https://example.com/a.png")
        self.assertEqual(
            _url_from_cell('=HYPERLINK("https://example.com/b.jpg","Portrait")'),
            "https://example.com/b.jpg",
        )
        self.assertIsNone(_url_from_cell("No url here"))

    def test_row_url_pair_uses_first_and_second_url_when_columns_unspecified(self):
        person_url, species_url = _row_url_pair(
            ["Alice", "Human", "https://example.com/p.png", "https://example.com/s.png"],
            None,
            None,
        )
        self.assertEqual(person_url, "https://example.com/p.png")
        self.assertEqual(species_url, "https://example.com/s.png")


@override_settings(MEDIA_ROOT="/tmp/cataclysm-test-media")
class DownloadSheetImagesCommandTestCase(TestCase):
    def test_command_downloads_and_saves_images(self):
        person = Person.objects.create(name="Alice", age=30, sex="F")
        species = Species.objects.create(species_name="Human")
        rows = [["Alice", "Human", "", "", "", "https://example.com/person.png", "https://example.com/species.jpg"]]

        mock_response = Mock()
        mock_response.content = b"image-bytes"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status = Mock()

        with (
            patch("cataclysm.management.commands.download_sheet_images.read_sheet_data", side_effect=[rows, []]),
            patch("cataclysm.management.commands.download_sheet_images.requests.get", return_value=mock_response) as mock_get,
        ):
            call_command(
                "download_sheet_images",
                spreadsheet_id="dummy-sheet",
                tabs=["Main Crew", "Other Crew"],
                person_url_col=5,
                species_url_col=6,
            )

        person.refresh_from_db()
        species.refresh_from_db()

        self.assertTrue(person.image.name)
        self.assertTrue(species.image.name)
        self.assertEqual(mock_get.call_count, 2)

    def test_dry_run_does_not_download_or_save(self):
        person = Person.objects.create(name="Alice", age=30, sex="F")
        species = Species.objects.create(species_name="Human")
        rows = [["Alice", "Human", "", "", "", "https://example.com/person.png", "https://example.com/species.jpg"]]

        with (
            patch("cataclysm.management.commands.download_sheet_images.read_sheet_data", side_effect=[rows, []]),
            patch("cataclysm.management.commands.download_sheet_images.requests.get") as mock_get,
        ):
            call_command(
                "download_sheet_images",
                spreadsheet_id="dummy-sheet",
                tabs=["Main Crew", "Other Crew"],
                person_url_col=5,
                species_url_col=6,
                dry_run=True,
            )

        person.refresh_from_db()
        species.refresh_from_db()

        self.assertFalse(person.image.name)
        self.assertFalse(species.image.name)
        self.assertEqual(mock_get.call_count, 0)
