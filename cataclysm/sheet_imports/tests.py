from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.test import TestCase

from people.models import Person

from .models import SheetImportRun, SheetRowBinding, SheetSource


class SheetImportModelTests(TestCase):
    def setUp(self):
        self.source = SheetSource.objects.create(
            spreadsheet_id='sheet-id',
            tab_name='Main Crew',
            range_name='A3:V',
        )

    def test_source_region_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SheetSource.objects.create(
                spreadsheet_id='sheet-id',
                tab_name='Main Crew',
                range_name='A3:V',
            )

    def test_row_binding_can_trace_a_person(self):
        person = Person.objects.create(name='A crew member', age_text='Unknown')
        run = SheetImportRun.objects.create(source=self.source)
        binding = SheetRowBinding.objects.create(
            source=self.source,
            last_run=run,
            row_fingerprint='a' * 64,
            source_row_number=3,
            status=SheetRowBinding.Status.IMPORTED,
            content_type=ContentType.objects.get_for_model(person),
            object_id=person.pk,
            raw_payload={'Name': person.name, 'Age': '?'},
            normalized_payload={'name': person.name, 'age': None},
        )

        self.assertEqual(binding.target, person)
        self.assertEqual(binding.raw_payload['Age'], '?')

    def test_binding_requires_both_target_fields(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            SheetRowBinding.objects.create(
                source=self.source,
                row_fingerprint='b' * 64,
                content_type=ContentType.objects.get_for_model(Person),
                raw_payload={},
            )
