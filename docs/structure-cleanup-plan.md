# Codebase structure cleanup plan

## Purpose

This plan proposes an incremental cleanup of CataclysmApp's repository and
Django structure. The goal is to make ownership obvious, reduce accidental
duplication, and add guardrails without coupling structural work to feature
changes. Each phase should be a small, independently reversible pull request.

## Current-state findings

### 1. The repository contains two Django projects

`cataclysm/` is the documented and deployed application, while `mysite/` is a
tracked Django tutorial project with its own database and `polls` app. Keeping
both at the repository root makes the supported entry point ambiguous and can
confuse tooling that discovers `manage.py`, settings modules, or tests.

### 2. Generated and runtime data is tracked

Although `.gitignore` excludes `cataclysm/staticfiles/`, files already tracked
under that directory remain in Git. The repository also tracks SQLite/runtime
data (`mysite/db.sqlite3`), uploaded media under `cataclysm/media/`, and an
intermediate JSON file under `cataclysm/temp_files/`. Generated assets obscure
source changes and increase repository size; uploaded campaign content needs an
explicit decision about whether it is source content or deployment data.

### 3. Project-level responsibilities are mixed

The inner `cataclysm/cataclysm/` package contains settings and URL routing, but
also shared views, template tags, Google Sheets integration, a large image
download command, and its tests. A second `cataclysm/utils/google_sheets.py`
compatibility module adds another apparent home for the same responsibility.
This makes the project configuration package behave like an application and
weakens ownership boundaries.

### 4. App interfaces are inconsistent

Some apps use namespaced REST-like URLs and class-based views, while `people`,
`species`, `party`, and `mindmaps` expose global URL names and inconsistent path
styles. `ships` and `vehicles` are installed placeholder apps with no models.
The conventions described in `ARCHITECTURE.md` therefore document existing
inconsistency rather than a single preferred structure.

### 5. A few modules have grown beyond one responsibility

`adminflow/views.py` combines several upload, import, duplicate-resolution, and
administrative workflows in one large module. The People app similarly combines
directory queries, saved views, CSV export, CRUD, and image handling across a
large view/template surface. These areas are difficult to navigate and likely
to attract unrelated changes.

### 6. Tooling does not enforce the intended structure

There is no `pyproject.toml`, lint/format configuration, pre-commit setup, or CI
workflow. Tests use a mixture of monolithic `tests.py` modules and split test
modules. `requirements.txt` is UTF-16 encoded, combines direct and transitive
runtime dependencies, and provides no separate development toolchain.

### 7. Runtime configuration is not environment-safe by default

The main settings module is monolithic, hard-codes `DEBUG = True`, and includes
an insecure development fallback secret. Local, test, and production concerns
should be explicit so cleanup work can be validated consistently in each
environment.

## Design principles

1. **One supported project:** one `manage.py`, one settings package, and one
   clearly documented application root.
2. **Apps own domain behavior:** models, forms, services, selectors, views,
   URLs, templates, and tests for a domain stay together.
3. **Configuration stays thin:** the Django project package owns settings,
   root routing, ASGI, and WSGI only.
4. **Generated state stays out of Git:** source assets are tracked; collected
   assets, databases, uploads, caches, reports, and secrets are not.
5. **Prefer consistent public interfaces:** every installed app has an
   `app_name`, predictable URL names, and app-scoped templates.
6. **Separate reads from workflows when complexity warrants it:** use small
   `selectors.py` modules for reusable query construction and `services.py` for
   imports, exports, and state-changing orchestration; do not introduce a
   generic abstraction before at least two callers need it.
7. **Move in tested slices:** add characterization tests before renames or
   moves, preserve compatibility temporarily, and remove compatibility code in
   a later change.

## Proposed target layout

```text
CataclysmApp/
├── .github/workflows/ci.yml
├── config/                       # Django project/configuration package
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── test.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                         # Domain Django apps
│   ├── people/
│   │   ├── services.py
│   │   ├── selectors.py
│   │   ├── views/
│   │   ├── templates/people/
│   │   └── tests/
│   ├── species/
│   ├── equipment/                # Optional later merge of armor/weapons
│   └── ...
├── common/                       # Proven cross-domain helpers only
│   ├── integrations/google_sheets.py
│   ├── templatetags/
│   └── tests/
├── templates/                    # Truly project-wide templates
├── static/                       # Source static assets
├── docs/
├── manage.py
├── pyproject.toml
└── requirements/                 # Or a lock-file-based dependency setup
    ├── base.txt
    └── development.txt
```

The `apps/` move is optional and should happen only after the higher-value
cleanup below. Django projects work well with top-level app packages; consistent
ownership matters more than adding nesting. Likewise, armor and weapons should
only become an `equipment` app if their domain behavior and data lifecycle are
actually shared.

## Phased implementation

### Phase 0 — Establish a baseline (highest priority, low risk)

- Record the supported Python and Django versions.
- Convert `requirements.txt` to UTF-8 and distinguish direct runtime
  dependencies from development/test dependencies. Use a reproducible lock or
  constraints file for transitive versions.
- Add `pyproject.toml` with one formatter/linter (for example Ruff), test
  configuration, and basic import-order rules.
- Add CI that installs dependencies and runs formatting/lint checks,
  `python manage.py check`, migration drift checks, and the full test suite.
- Add a small test-settings module using a temporary SQLite database and local
  memory/console integrations.
- Capture route names and critical import paths in characterization tests before
  moving modules.

**Exit criteria:** a clean checkout has one documented command that reproduces
all automated checks, and CI runs that command.

### Phase 1 — Remove repository ambiguity (highest priority, low risk)

- Delete `mysite/` after confirming it is not referenced by deployment or
  documentation.
- Remove tracked `cataclysm/staticfiles/` content from the Git index and verify
  `collectstatic` recreates it during build/deployment.
- Remove the tracked SQLite database and intermediate `temp_files` artifacts;
  expand ignore rules to cover runtime databases, temporary reports, coverage,
  editor files, and local environment files.
- Decide whether campaign images are curated source fixtures or user uploads.
  If curated, move them to a named source-content/static location with ownership
  documented. If uploaded, remove them from Git and document persistent media
  storage and backup requirements.
- Update `README.md`, `ARCHITECTURE.md`, Docker files, and commands so every
  example uses the single supported project root.

**Exit criteria:** the repository has one application entry point and contains
no generated build output or unexplained runtime state.

### Phase 2 — Make configuration explicit (high priority, medium risk)

- Split settings into `base`, `development`, `test`, and `production` modules,
  keeping shared values in `base` and security-sensitive defaults in
  `production`.
- Read `DEBUG`, secret key, allowed hosts, database location, email, media, and
  proxy/TLS options through a small, consistently validated environment layer.
- Fail fast in production when required secrets or hosts are absent; permit
  safe convenience defaults only in development/test settings.
- Keep the project package limited to configuration and root routing. Move
  template tags and Google Sheets helpers to a `common` app/package, and move
  feature-specific management commands to the app that owns their workflow.
- Remove the legacy Google Sheets compatibility module after all imports point
  to the canonical location and tests protect the public API.

**Exit criteria:** development, tests, and production select explicit settings;
the configuration package contains no domain workflows.

### Phase 3 — Normalize app contracts (high priority, medium risk)

- Add `app_name` to every app URL configuration and update reverse calls and
  templates to use namespaced names.
- Choose a consistent URL vocabulary (`add`, `<pk>`, `<pk>/edit`,
  `<pk>/delete`) and use `pk` consistently. Preserve redirects or aliases for
  bookmarked legacy routes for one release where necessary.
- Namespace templates by app (for example
  `people/templates/people/person_detail.html`) to prevent collisions such as
  generic `add_object.html` and `index` names.
- Standardize CRUD on generic class-based views where this removes boilerplate;
  retain function views for workflow endpoints where functions remain clearer.
- Either implement and test `ships`/`vehicles` as real domain apps, or remove
  them from `INSTALLED_APPS` and expose an explicit “coming soon” page without
  pretending they provide CRUD.
- Document one convention for pagination, query optimization, forms,
  permissions, success URLs, and template naming, then enforce it in review.

**Exit criteria:** app URLs and templates cannot collide, placeholder status is
explicit, and the architecture guide describes a single default convention.

### Phase 4 — Decompose workflow hotspots (medium priority, medium risk)

- Split `adminflow/views.py` into focused view modules such as `imports.py`,
  `images.py`, and `duplicates.py`; keep shared orchestration in services owned
  by `sheet_imports`, `people`, or `species` rather than by the admin UI.
- Split People directory filtering/query construction into selectors, CSV and
  saved-view operations into services, and CRUD/directory/export endpoints into
  focused view modules.
- Break large templates into app-local partials for filter controls, result
  tables, saved views, and scripts. Keep JavaScript in source static files when
  it is not dependent on server-rendered values.
- Review query counts around lists/details and add query-count regression tests
  before changing prefetch/select-related behavior.
- Split large `tests.py` files into `tests/test_models.py`, `test_views.py`,
  `test_services.py`, and `test_commands.py`, with factories/builders local to
  each app or in a deliberately small shared test helper.

**Exit criteria:** view functions primarily adapt HTTP input/output; business
workflows are directly unit-testable; no module is split merely to satisfy an
arbitrary line limit.

### Phase 5 — Consolidate only proven duplication (lower priority)

- Compare armor, weapons, and other catalog apps for genuinely identical CRUD,
  permission, and template behavior. Extract a shared mixin or merge domains
  only when it reduces repeated policy—not simply repeated syntax.
- Review `tags`, `landing`, and `adminflow` model modules for empty or misplaced
  app scaffolding and remove unused files/apps where Django does not require
  them.
- Reassess whether an `apps/` namespace improves navigation enough to justify
  migration churn. If adopted, perform it as a mechanical change with no domain
  redesign in the same pull request.
- Add lightweight architecture checks (for example, forbidden imports from UI
  modules into domain services) only after stable boundaries emerge.

**Exit criteria:** shared code represents stable concepts with multiple real
callers, and imports make dependency direction clear.

## Recommended pull-request sequence

1. **Tooling baseline:** encoding/dependencies, `pyproject.toml`, test settings,
   CI, and contributor commands.
2. **Repository hygiene:** remove `mysite`, collected static files, database,
   and temporary artifacts; clarify media policy.
3. **Settings split:** introduce environment-specific settings without moving
   apps.
4. **Shared-code ownership:** move Google Sheets and template-tag code with
   compatibility imports, then remove the compatibility layer separately.
5. **URL/template namespaces:** migrate one app at a time, starting with the
   smaller apps, with redirect/reverse tests.
6. **Adminflow decomposition:** move workflows to owning apps and split views.
7. **People decomposition:** selectors/services/view modules/template partials.
8. **Placeholder decision:** implement or remove ships and vehicles.
9. **Optional package/domain consolidation:** evaluate `apps/` and `equipment`
   only after earlier boundaries are stable.

## Validation checklist for every structural pull request

- Run formatter and linter checks.
- Run `python manage.py check` under development and production-like settings.
- Run `python manage.py makemigrations --check --dry-run`.
- Run the complete test suite, plus focused tests for moved code.
- Confirm every documented URL reverses and legacy aliases behave as promised.
- Build the container and run its health/startup path.
- Run `collectstatic --noinput` into an empty temporary directory.
- Verify `git status` remains clean after tests, startup, and asset collection.
- For template/static changes, smoke-test key pages at desktop and narrow
  viewport sizes.

## Risks and mitigations

- **Import and migration identity changes:** moving Django apps can change app
  labels and migration dependencies. Avoid changing app labels; defer the
  optional `apps/` namespace until tests and backups are in place.
- **Broken bookmarked routes:** namespace/path cleanup can break external links.
  Add route-level tests and temporary redirects/aliases, with a documented
  removal date.
- **Lost media or local data:** classify and back up tracked media/databases
  before removal; provide seed fixtures only for data needed by tests or demos.
- **Large noisy diffs:** do not combine formatting, file moves, and behavior
  changes. Land mechanical changes separately and use `git diff --color-moved`
  during review.
- **Premature abstractions:** prefer consistent duplication over a generic base
  layer until shared policy is demonstrated by multiple apps.

## Success measures

- A new contributor can identify the only supported entry point and run all
  checks from the README in under ten minutes (excluding dependency download).
- Running tests, the server, and `collectstatic` does not modify tracked files.
- Every route and template is app-namespaced, except intentionally global
  project pages.
- Production starts only with explicit secure configuration.
- Domain workflows can be tested without constructing HTTP requests.
- The largest workflow modules trend downward while test coverage and query
  regression coverage trend upward.
