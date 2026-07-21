from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SheetSource(models.Model):
    spreadsheet_id = models.CharField(max_length=128)
    tab_name = models.CharField(max_length=100)
    range_name = models.CharField(max_length=100, blank=True)
    schema_version = models.PositiveIntegerField(default=1)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('spreadsheet_id', 'tab_name', 'range_name'),
                name='unique_sheet_source_region',
            ),
        ]
        indexes = [models.Index(fields=('spreadsheet_id', 'tab_name'))]

    def __str__(self):
        region = f'!{self.range_name}' if self.range_name else ''
        return f'{self.tab_name}{region}'


class SheetImportRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'

    source = models.ForeignKey(SheetSource, on_delete=models.PROTECT, related_name='runs')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    dry_run = models.BooleanField(default=True)
    content_fingerprint = models.CharField(max_length=64, blank=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    counts = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.source} ({self.get_status_display()})'


class SheetRowBinding(models.Model):
    class Status(models.TextChoices):
        IMPORTED = 'imported', 'Imported'
        UNRESOLVED = 'unresolved', 'Unresolved'
        REJECTED = 'rejected', 'Rejected'
        STALE = 'stale', 'Stale'

    source = models.ForeignKey(SheetSource, on_delete=models.CASCADE, related_name='row_bindings')
    last_run = models.ForeignKey(
        SheetImportRun,
        on_delete=models.SET_NULL,
        related_name='row_bindings',
        null=True,
        blank=True,
    )
    row_fingerprint = models.CharField(max_length=64)
    source_row_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UNRESOLVED)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    raw_payload = models.JSONField(default=dict)
    normalized_payload = models.JSONField(default=dict, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('source', 'row_fingerprint'),
                name='unique_sheet_source_row_fingerprint',
            ),
            models.CheckConstraint(
                check=(
                    models.Q(content_type__isnull=True, object_id__isnull=True)
                    | models.Q(content_type__isnull=False, object_id__isnull=False)
                ),
                name='sheet_binding_target_pair',
            ),
        ]
        indexes = [
            models.Index(fields=('content_type', 'object_id')),
            models.Index(fields=('source', 'status')),
        ]

    def __str__(self):
        return f'{self.source}: row {self.source_row_number or "?"}'
