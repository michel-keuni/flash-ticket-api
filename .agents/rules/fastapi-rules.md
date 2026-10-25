---
trigger: always_on
---

# AGENTS.md — FastAPI Engineering Standards

## 1. General Principles

- **Framework:** FastAPI.
- **Python:** 3.11+ unless the project specifies a compatible version.
- **Validation:** Pydantic v2.
- **ORM:** SQLAlchemy 2.0 when a relational database and ORM are appropriate.
- **Database:** PostgreSQL by default for relational projects, unless another database is explicitly justified.
- **Migrations:** Alembic when using SQLAlchemy with a schema-managed relational database.
- **Testing:** pytest and HTTPX.
- **Code quality:** Ruff for linting and formatting.
- **Configuration:** Centralized settings, loaded from environment variables or an approved secrets manager.

Prioritize correctness, security, maintainability, testability, observability, and simplicity over unnecessary abstraction.

Do not introduce technologies, dependencies, architectural patterns, or infrastructure without a clear project requirement.

Before implementing a feature, inspect the existing project structure, dependencies, conventions, and relevant tests. Preserve established patterns unless a change is justified.

## 2. Architecture and Separation of Responsibilities

Keep the architecture modular and ensure that each layer has a clearly defined responsibility.

Recommended structure:

    app/
    ├── main.py
    ├── api/
    │   └── v1/
    │       ├── router.py
    │       └── endpoints/
    ├── core/
    │   ├── config.py
    │   ├── security.py
    │   ├── logging.py
    │   └── exceptions.py
    ├── db/
    │   ├── session.py
    │   └── base.py
    ├── models/
    ├── schemas/
    ├── services/
    ├── repositories/
    └── tests/


## 3. Database & Migrations
- Use modern SQLAlchemy 2.0 conventions and explicit database constraints.
- Choose synchronous or asynchronous database access according to project requirements. Never block the event loop with synchronous I/O inside `async def` handlers.
- Manage transactions explicitly and handle rollbacks correctly.
- Whenever database models change, assess migration requirements and review Alembic migrations before applying them.
- Never perform destructive database operations without checking their impact.

## 4. Security & Configuration
- Every protected endpoint must enforce authentication and appropriate authorization.
- Never hardcode secrets. Load configuration through centralized settings and environment variables or a secrets manager.
- Never store plaintext passwords or expose sensitive information in API responses or logs.
- Validate all external inputs and enforce resource-level permissions where necessary.
- Configure CORS, token validation, rate limiting and file access according to project requirements.

## 5. Coding Practices & Error Handling
- Use modern Python type hints (`str | None` instead of `Optional[str]` where appropriate).
- Use `httpx.AsyncClient` for asynchronous HTTP requests.
- Handle exceptions explicitly and return appropriate HTTP status codes.
- Use structured logging instead of `print()` in production.
- Avoid unnecessary dependencies, duplicated logic and premature abstractions.
- Keep code modular, readable and maintainable.

## 6. Testing & Quality
- Write tests for business logic, API endpoints, authentication and critical error cases.
- Run relevant tests and quality checks after changes.
- Never claim that tests pass unless they have actually been executed.
- Update documentation when API contracts or setup instructions change.


