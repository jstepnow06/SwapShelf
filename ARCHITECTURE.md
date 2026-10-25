# SwapShelf Architecture

## System overview

```mermaid
flowchart TD
    Browser[Web browser]
    Web[Gunicorn / Django WSGI]
    URLs[swapshelf/urls.py]
    Market[market views and templates]
    Auth[Django authentication and sessions]
    Static[Django static-file route]
    DB[(SQLite database)]
    Files[market/static/market/style.css]
    Volume[Docker data volume]

    Browser -->|HTTP requests| Web
    Web --> URLs
    URLs --> Market
    URLs --> Auth
    URLs --> Static
    Static --> Files
    Market --> DB
    Auth --> DB
    DB --> Volume
```

SwapShelf is a server-rendered Django application. Browsers submit HTTP requests to
Gunicorn, which invokes the Django WSGI application. Django routes requests to the
market views, authentication views, or the static-file route. Views render HTML
templates and read or write application data in SQLite.

## Repository structure

| Component | Location | Responsibility |
|---|---|---|
| Django project configuration | `swapshelf/` | Settings, URL routing, WSGI entry point |
| Marketplace application | `market/` | Listings, profiles, messaging, desk page |
| Data models | `market/models.py` | `Listing`, `Thread`, and `Message` tables |
| Forms | `market/forms.py` | Listing and profile input validation |
| Templates | `market/templates/market/` | Server-rendered HTML pages |
| Static assets | `market/static/market/` | CSS served at `/static/` |
| Database | `data/swapshelf.db` | SQLite application data |
| Container setup | `Dockerfile`, `docker-compose.yml` | Python runtime, Gunicorn, persistent data volume |

## Request flow

1. A browser sends a request to the application on port `3000`.
2. Gunicorn loads `swapshelf.wsgi`.
3. `swapshelf/urls.py` routes the request:
   - `/admin/` to Django admin.
   - `/logout/` to Django's logout view.
   - `/static/<path>` to Django's static-file view.
   - All other application paths to `market/urls.py`.
4. A market view:
   - Checks authentication where required.
   - Loads or validates model data.
   - Applies authorization checks for protected mutations.
   - Renders a template or redirects.
5. Django's session middleware maintains the logged-in user's session.

## Main data model

```mermaid
erDiagram
    USER ||--o{ LISTING : owns
    USER ||--o{ THREAD : buys
    LISTING ||--o{ THREAD : receives
    THREAD ||--o{ MESSAGE : contains
    USER ||--o{ MESSAGE : sends

    USER {
        integer id PK
        string username
        string email
        boolean is_staff
    }
    LISTING {
        integer id PK
        integer owner_id FK
        string title
        text description
        decimal price
        string category
        string status
        text seller_note
        datetime created_at
    }
    THREAD {
        integer id PK
        integer listing_id FK
        integer buyer_id FK
        datetime created_at
    }
    MESSAGE {
        integer id PK
        integer thread_id FK
        integer sender_id FK
        text body
        datetime created_at
    }
```

## Authentication and authorization

- Public pages include the board and listing details.
- Registration and login use Django authentication.
- `@login_required` protects posting, profile, messaging, listing management,
  and the department desk.
- Listing edit, mark-sold, and delete operations query by both listing ID and
  `owner=request.user`, so only the poster can mutate a listing.
- The profile form intentionally excludes `User.is_staff`; users cannot promote
  themselves through the application.
- The desk view checks `request.user.is_staff`.
- Django admin remains available at `/admin/` for trusted staff accounts.

## Deployment

```mermaid
flowchart LR
    Client[Browser] -->|TCP :3000| Container[Docker web container]
    Container --> Gunicorn[Gunicorn]
    Gunicorn --> Django[Django WSGI app]
    Django --> DB[(SQLite)]
    DB --> Volume[swapshelf-data volume]
```

The container uses Python 3.12, installs the pinned dependencies, runs database
migrations and seed data on startup, and starts Gunicorn on `0.0.0.0:3000`.
The SQLite database is stored under `/app/data` and persists through the
`swapshelf-data` Docker volume.
