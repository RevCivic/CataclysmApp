# Nimbus Crew spreadsheet import and discovery plan

## Scope and snapshot

This plan is based on a workbook export of the shared **Nimbus Crew** Google
Sheet (`1XRyeXDIhNE6iwTXS_zDc_eHrQFU96Z2OUCIXm_t0twE`) inspected on
2026-07-21. It covers every tab, how its data relates to a character, and an
incremental path from today's one-way crew loader to repeatable imports,
dynamic searches, and saved table views.

The spreadsheet should remain the authoring source during the transition, but
the application database should become the query source. Searching a live
sheet on every request would be slow, brittle, and unable to provide reliable
relationships or permissions.

## Workbook inventory

The workbook contains 12 tabs. Row counts below are non-empty rows in the
export and include headings, notes, and side tables; they are not record
counts.

| Tab | Observed shape | Character relationship | Import recommendation |
| --- | --- | --- | --- |
| **Main Crew** | 41 non-empty rows; name/species/age/sex, 14 trait flags, rank, job, branch, condition | One primary character per row | Import first into `Person`, membership/assignment, traits, and status. Its headings are on rows 1-2 and data starts on row 3. |
| **Other Crew** | 812 non-empty rows; 16 trait flags, rank/job/branch, health, origin/destination/reason, and physical descriptors | One character per row | Import first with Main Crew. Headings are split across rows 2 and 4 and data starts around row 6; blank and section rows must be rejected by validation rather than assumed to be people. |
| **Departments** | 3,055 non-empty rows; multiple independent name/role lists and ship/clan/department blocks placed side-by-side | Assignments and group membership | Import after crew identity matching. Treat each visually separate block as a configured table, not the entire rectangular tab as one table. |
| **Stats** | 846 non-empty rows; name plus 59 capability/category flags from Command through Cook | Many searchable capabilities per character | Normalize headings into tags/capabilities and create a through record carrying the source and raw marker (`X`, letter, etc.). Do not add 59 boolean fields. |
| **Assets** | 58 non-empty rows; pets/owners plus vehicle/hangar/equipment side tables | Owned pets/assets or operational assets | Split into configured regions. Link owners to people only after identity resolution; keep unresolved owner text. Vehicles can later bind to a vehicle model when that app has one. |
| **Family** | 341 non-empty rows; four side-by-side relationship/family blocks with repeated gender, relationship, family, children, location, and notes columns | Person-to-person and family relationships | Convert each configured block to relationships/family groups. This is not a conventional row table and needs block-specific parsing plus manual review. |
| **Kids** | 274 non-empty rows; child, sex, age, birthday, species, family, parents, location, notes, and calculated full name | Characters and parent relationships | Import children as people only when desired by policy, then link parent relationships. The calculated full-name column must not be treated as an immutable ID. |
| **Equipment** | 30 non-empty rows; weapons, ammunition, and armor in side-by-side three-column tables | Inventory/catalog data, not consistently person-owned | Split into three regions and upsert catalog items. Add ownership/assignment only if a later sheet supplies it. |
| **Random** | 17 non-empty rows and 28 formulas; volatile random selections and save columns | Derived convenience output | Do not import. Recreate as a database-powered random crew query if useful. |
| **Quarters** | 263 non-empty rows; name, room, section, direction, type, plus layout notes at the right | Accommodation assignment | Import the A:E table as an assignment/location record; ignore the ship-layout calculation region. |
| **Supers** | 211 non-empty rows; hero name, real name, race, multiline powers; section headings occur within the data | Alias and ability data | Import aliases and powers after matching real names. Preserve unknown real names and category headings without creating false people. |
| **List** | 891 non-empty rows and 891 formulas; a calculated name list | Derived index | Do not import. Replace with a query over imported people. |

### Important inconsistencies found

* Main Crew maps columns E:R to 14 traits, but Other Crew maps E:T to 16;
  Other Crew has Arcane and Divine before Flier and Mutant. The existing fixed
  column map therefore cannot safely serve both tabs.
* The two crew tabs use different column positions for rank/job/branch and call
  the status field `Condition` versus `Health`.
* Age is not reliably numeric (examples include inequalities, `?`, and status
  text), while `Person.age` currently requires an integer.
* Names are reused as joins across nearly every tab, but names are neither
  unique nor stable. Some values are aliases, possessives, partial names,
  composite identifiers, or apparent numeric identifiers.
* Several tabs contain multiple unrelated tables in the same grid. Inferring a
  schema from the first non-empty row will silently combine unrelated data.
* Formula-driven tabs and columns (`Random`, `List`, and the Kids full-name
  column) are derived values and should not be authoritative inputs.
* Free-text spelling and vocabulary vary (`Job`/`Position`,
  `Condition`/`Health`, and department spelling variants). Imports must retain
  raw source values even when a normalized value is available.

## Current application gap analysis

The current loader reads one configured A1 range and always creates a new
`Person`. It defaults unparseable ages to `1`, does not bind species, faction,
branch, status, origin, departments, stats, family, quarters, aliases, or
assets, and has no durable source-row identity. Re-running it therefore risks
duplicates and silent data loss. Its trait mapping also reflects Main Crew's
14-column layout while the default range points at Other Crew.

The current person list supports name text, tag filtering, sorting, and
pagination. This is a useful base, but it cannot express questions such as
“healthy engineers on Potempkin,” “all pilots with quarters in section B,” or
“crew related to this person,” because those fields and relationships are not
represented consistently in the database.

The image command and Google Sheets utility should be retained: URL/ID parsing,
public CSV access, and rich-cell hyperlink extraction are reusable. Import
orchestration, parsing, validation, identity resolution, and persistence
should be separate layers rather than added to the transport helper.

## Target data model

Use a small normalized core and preserve provenance. Exact naming can be
adjusted during implementation, but the concepts should remain separate.

### Identity and provenance

* **Person**: keep the character record; make age nullable and add `age_text`
  (or a structured min/max/qualifier representation) so the source is not
  falsified. Consider lengthening short free-text fields.
* **PersonAlias**: `person`, `name`, `kind` (hero, nickname, former name), and
  optional source reference.
* **SheetSource**: spreadsheet ID, tab, configured region/range, parser schema
  version, and enabled flag.
* **SheetImportRun**: source, start/end timestamps, workbook revision/fingerprint,
  mode, counts, and outcome.
* **SheetRowBinding**: run/source, stable row fingerprint, source row number,
  target content type/object ID, raw payload JSON, normalized payload JSON,
  warnings, and last-seen timestamp. Row number is diagnostic, not identity.
* **IdentityAlias**: normalized source name to one `Person`, with match status
  and reviewer. This makes subsequent imports deterministic without forcing
  `Person.name` to be unique.

### Queryable character facts

* **Capability** and **PersonCapability**: normalized Stats headings and trait
  flags, with category, raw marker, source, and confidence. Existing `Trait`
  records can either become the user-curated subset or be unified with this
  vocabulary after a migration decision.
* **OrganizationUnit**: ship, branch, department, clan, or team in a hierarchy.
* **PersonAssignment**: person, unit, role/job, rank, status, start/end (when
  known), and source. This avoids overwriting one `Person.position` when a
  person has several roles.
* **PersonRelationship**: from/to person, relationship type, family/group,
  notes, source, and unresolved target text when no safe match exists.
* **AccommodationAssignment**: person, room, section, direction, room type,
  and source.
* **PersonProfileFact** (optional transitional model): typed key/value facts
  for origin, destination, reason, height, weight, and colors until frequently
  queried facts earn dedicated fields. Store normalized and display values.
* **Asset** and **PersonAsset**: type, name/model/species, purpose, quantity,
  owner/assignee, status, and source. This can bridge to future ship/vehicle
  models rather than blocking the crew import.

Add database indexes on normalized person name, capability, organization unit,
status, rank, location, and the foreign keys used by filters. Keep imported
facts distinct from manually curated tags so a sync cannot erase editorial
work.

## Import architecture

Build a schema-driven pipeline with five explicit stages:

1. **Extract** – extend the Sheets utility with workbook metadata/tab listing
   and batched value reads. Use the Sheets API when credentials are available;
   retain public CSV/rich-cell fallbacks. Capture a revision or content hash.
2. **Parse** – define a parser configuration per tab and region: heading rows,
   data start, column names, block coordinates, sentinel/section rows, and
   field transforms. Parsers return typed data-transfer objects and never
   write models.
3. **Validate and normalize** – normalize whitespace and lookup vocabulary,
   parse safe numeric values, retain every raw value, identify formula/derived
   fields, and produce row-level errors/warnings. Never convert unknown ages to
   a fabricated value.
4. **Resolve identity** – match in order: approved row binding, approved alias,
   exact normalized canonical name, then a review candidate. Do not
   automatically accept fuzzy name matching. Species and organization values
   follow the same controlled resolution pattern.
5. **Apply** – transactionally upsert by bindings/natural keys, add source-owned
   facts, and mark missing source records stale. Deletion is a separate,
   explicit option. A failed row must not partially update its relationships.

Each parser should be independently testable with checked-in, anonymized
fixtures. Do not commit a full production workbook export: it changes often,
contains campaign data that may be sensitive, and makes tests difficult to
review.

## Operator workflow and safety

Provide one management command initially, for example:

```text
python manage.py import_crew_workbook \
  --spreadsheet-id <URL-or-ID> \
  --tabs "Main Crew" "Other Crew" \
  --dry-run --report-json import-report.json
```

Required command behavior:

* Dry-run by default until an explicit `--apply` is supplied.
* Select tabs/regions and import phases; never assume all tabs have one schema.
* Print created/updated/unchanged/stale/unresolved/error counts per tab.
* Emit a machine-readable report without including credentials or image bytes.
* Support `--strict` to roll back on any invalid row and normal mode to use
  per-row savepoints while reporting rejected rows.
* Record the schema version and content fingerprint, and make an unchanged
  rerun a no-op.
* Never delete people or curated relations merely because a row disappeared.
  Offer a reviewed `--archive-missing` operation later.
* Require an identity-review step for ambiguous names, apparent headings,
  aliases with no real name, and parent/owner references that do not match.

After the CLI is stable, add a staff-only import screen showing a preview and
diff, unresolved identities, row errors, prior runs, and an explicit apply
confirmation. The worker should run out of the request/response cycle for a
large workbook.

## Search, custom views, and tables

### Search API/query service

Create a single `PersonFilter`/query service used by both HTML and any future
JSON API. It should support:

* free text across canonical name, aliases, species, role, unit, and selected
  profile facts;
* multi-select filters for species, traits/capabilities, branch/ship/department,
  rank, role, health/status, location/origin, accommodation, relationship, and
  asset;
* explicit AND/OR behavior for multiple capabilities;
* safe allow-listed sorting, including related display fields;
* `select_related`/`prefetch_related` plans and `distinct()` only when needed;
* URL-encoded filters so searches are shareable and browser navigation works.

Do not accept arbitrary model field names in `order_by`; the current view's
direct query-parameter ordering should be replaced by an allow-list as part of
this work.

### Saved custom views

Add **SavedPersonView** with owner, name, visibility (private/shared), filter
JSON, selected columns, sort list, page size, and schema version. Validate its
JSON against an allow-list so saved views cannot expose hidden fields or build
arbitrary ORM lookups. Include migration logic when filter/column identifiers
are renamed.

Start with these useful presets:

* Crew directory: name, species, rank, role, branch, status, current unit.
* Skills matrix: rows are people; selected capabilities are compact columns.
* Department roster: unit/department grouping with rank and role.
* Quarters manifest: room/section/direction/type and occupants.
* Family directory: person, relationship, related person, location, notes.
* Super identities: alias, real name, species, and powers/capabilities.

Render normal directories server-side with pagination and accessible table
markup. For the wide skills matrix, allow horizontal scrolling, sticky name
and header cells, a column chooser, and CSV export of the filtered result. All
queries and exports must apply the same hidden-record and authorization rules.

## Delivery phases and acceptance criteria

### Phase 0 – characterization and contracts

* Freeze anonymized fixtures for every tab/region and document parser maps.
* Add tests demonstrating the current age, trait-offset, and duplicate-rerun
  failures before replacing the loader.
* Agree on whether kids, unknown supers, pets, and named assets are full people
  or related records.

**Accept when:** every observed grid region is classified as imported,
derived/ignored, or deferred; no tab is silently omitted.

### Phase 1 – safe crew core

* Add provenance/import-run/binding models and age/raw-value support.
* Implement schema-driven Main Crew and Other Crew parsers.
* Upsert people, species links, traits/capabilities, rank/role/branch/status,
  origin, and physical facts through reviewed identity mappings.
* Replace or deprecate `update_database_from_sheet`; share transport code with
  the image importer.

**Accept when:** dry-run explains every source row; applying twice creates no
duplicates and the second run is unchanged; malformed rows retain diagnostics;
manual tags/images/bios are untouched.

### Phase 2 – discovery experience

* Introduce the allow-listed query service and filters.
* Add configurable columns, URL-shareable searches, presets, CSV export, and
  saved private/shared views.
* Add query-count and pagination tests for large crew lists.

**Accept when:** the example cross-field searches above work, saved views round
trip, invalid filters are rejected, and a page does not perform per-person
queries.

### Phase 3 – character enrichment

* Import Stats, Departments, Quarters, Supers, Kids, and Family in that order.
* Provide an identity-resolution queue and staff reconciliation UI.
* Recreate Random and List as database queries rather than imports.

**Accept when:** all accepted references are linked, unresolved references are
visible and non-destructive, and relationship/capability/quarters presets agree
with reviewed fixtures.

### Phase 4 – assets and operations

* Import Assets and Equipment regions and integrate future vehicle/ship models.
* Move large imports to a background job, add scheduling/locking, audit and
  retention policy, failure notifications, and operational metrics.

**Accept when:** concurrent imports cannot overlap, failures are resumable or
safe to rerun, and operators can trace every imported value to its tab and row.

## Decisions needed before implementation

1. Is the sheet authoritative for existing manually edited Person fields, or
   should conflicts always require review?
2. Should a character who appears in both crew tabs have multiple assignments,
   and which tab decides their primary display status?
3. Are children and supers with unknown/alias-only identities intended to
   appear in the main person directory?
4. Which workbook values are sensitive, and should shared saved views/exports
   hide family, quarters, health, or physical descriptors from non-staff users?
5. Is the user willing to add a stable `character_id` column to source tabs?
   This is strongly recommended; an immutable ID dramatically reduces name
   matching and reconciliation risk.
6. Should spreadsheet deletions archive imported assignments/facts, or only
   mark them stale for manual review?

The best first implementation slice is Phase 0 plus a dry-run-only Phase 1
parser. It delivers a trustworthy diff and exposes identity/data-quality
decisions before any production data is changed.
