from django.contrib import admin

from .models import SheetImportRun, SheetRowBinding, SheetSource


@admin.register(SheetSource)
class SheetSourceAdmin(admin.ModelAdmin):
    list_display = ('tab_name', 'range_name', 'schema_version', 'enabled', 'updated_at')
    list_filter = ('enabled', 'schema_version')
    search_fields = ('spreadsheet_id', 'tab_name', 'range_name')


@admin.register(SheetImportRun)
class SheetImportRunAdmin(admin.ModelAdmin):
    list_display = ('source', 'status', 'dry_run', 'created_at', 'finished_at')
    list_filter = ('status', 'dry_run')
    readonly_fields = ('created_at',)


@admin.register(SheetRowBinding)
class SheetRowBindingAdmin(admin.ModelAdmin):
    list_display = ('source', 'source_row_number', 'status', 'target', 'last_seen_at')
    list_filter = ('status', 'source')
    search_fields = ('row_fingerprint',)
    readonly_fields = ('first_seen_at', 'last_seen_at')
