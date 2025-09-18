# Copilot / AI agent instructions for Absheron

Quick orientation
- This is a small Django (5.2) site that serves a personal website. Key apps: `core` (models, sanitization), `main` (views, templates, routing). There's also a `content` app present but most public site behavior uses `core` + `main`.
- DB: SQLite (`db.sqlite3`) and default Django ORM. Media files live in `media/`, static collected to `staticfiles/`.

What the agent should know (high-value facts)
- Models and data flow live in `core/models.py`. Important models: `Text`, `Image`, `Tag`, `Node`, and the through models `NodeText` / `NodeImage`.
  - `Text.clean()` sanitizes `body` using `bleach.Cleaner` and `bleach.linkify`. Prefer re-using `cleaner` and follow the existing allowed tags/attrs when generating or validating HTML.
  - `Image.file` is an `ImageField` saved under `media/images/`.
- Views use simple function-based views in `main/views.py`. Patterns to reuse:
  - Use `select_related()` and `prefetch_related()` as in `index()` and other list/detail views to avoid N+1 queries.
  - Pagination uses `django.core.paginator.Paginator` with page sizes: texts=10, images=24.
  - Node tree resolution uses `_resolve_node_by_path()` (look up `Node` by parent+slug chain) and returns root listing or a node detail with `texts` and `images` related to the node.
- Templates: see `main/templates/main/*` and `templates/base.html`. Templates sometimes rely on safe-rendered HTML stored in `Text.body` (see `{{ t.body|truncatechars_html:200|safe }}` in `main/index.html`). Keep sanitization rules in mind.
- Settings: `absheron/settings.py` shows DEBUG=True, SQLite DB, `STATIC_ROOT` and `MEDIA_ROOT` configured. `ckeditor` is installed and configured via `CKEDITOR_CONFIGS`.

Developer workflows and quick commands
- Normal dev run (from repo root):

  ```bash
  python -m venv .venv            # create virtualenv (convention)
  source .venv/bin/activate
  pip install -r requirements.txt  # if present; otherwise install Django and Pillow, bleach, ckeditor
  python manage.py migrate
  python manage.py runserver
  ```

- If `requirements.txt` is missing, install minimal dev deps:

  ```bash
  pip install Django==5.2.5 Pillow bleach django-ckeditor
  ```

- The project uses `sqlite3` (file `db.sqlite3`). Use `python manage.py dbshell` or `sqlite3 db.sqlite3` for quick DB inspection.
- Static files are expected to be collected into `staticfiles/` (already present). To re-generate:

  ```bash
  python manage.py collectstatic --noinput
  ```

Project-specific conventions and gotchas
- HTML sanitization: all free-form HTML for `Text.body` is sanitized in `core.models.clean()` via `bleach.Cleaner` with a curated `ALLOWED_TAGS` / `ALLOWED_ATTRS`. Do not bypass this; any code that creates `Text.body` should either call `.full_clean()` on the model or rely on the admin/forms which call `clean()`.
- Linkification: `bleach.linkify()` is used after cleaning. Avoid double-escaping or re-linkifying content in templates.
- Node path resolution: URLs like `/tree/a/b/c` are resolved by splitting slugs and querying `Node` by `parent` + `slug`. If writing code that manipulates node URLs, use `Node.get_absolute_url()` or `path_slugs` to keep behavior consistent.
- Templates truncate HTML with `truncatechars_html` and mark safe (`|safe`) — rely on the model sanitization to keep this secure.
- Tests: minimal test modules exist (`core/tests.py`, `main/tests.py`, `content/tests.py`) but coverage is small. When introducing code that touches models, add a focused test that exercises `clean()` and node resolution.

Integration points / external dependencies
- Third-party packages: `ckeditor` (WYSIWYG on admin), `bleach` (HTML sanitization), Pillow (for image handling) — ensure these are installed in the environment.
- No external APIs are called from the codebase (no HTTP clients present). Media and static files are local.

What to change and how to present patches
- Small, focused changes preferred. Follow repository style:
  - Keep function-based views in `main/views.py` for similar features.
  - Use `select_related()`/`prefetch_related()` where appropriate.
  - Update migrations when changing models (`python manage.py makemigrations` / `migrate`).
- When touching templates, respect existing CSS classes and inline styles in `templates/` and `staticfiles/`.

Files to inspect for more context
- `core/models.py` — sanitization and models
- `main/views.py` — routing and data access patterns
- `main/templates/main/index.html` — example of safe HTML rendering and tag filters
- `absheron/settings.py` — runtime configuration and installed apps

If anything is unclear
- Ask for the preferred Python/Django versions, target deployment (production vs development), and whether `requirements.txt` should be added to pin dependencies.

End of file
