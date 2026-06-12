# ERP Workflow Module — FGL Take-Home Assessment

> **Option Selected:** Option 1 — ERP Workflow Module
> **Candidate:** Arafat (Senior Software Engineer / Backend Team Lead)
> **Submission Deadline:** Sunday, 14 June 2026 at 09:00 AM (Asia/Dhaka)

---

## What I Built

A small but complete internal ERP workflow system for a **Sales → Accounts → Management** billing approval pipeline. The system allows:

- **Sales** staff to raise billing requests against clients.
- **Accounts** to review, approve, or reject those requests with notes.
- **Management** to view approved invoices in a dashboard with summary metrics.
- Full audit trail on every status change and action.

The focus is on a clear, auditable workflow with sensible role-based access and a real sense of product thinking — not a large system, but a cohesive one.

---

## Key User Flows

### 1. Sales — Raise a Billing Request
1. Log in as a Sales user.
2. Navigate to **New Request**.
3. Fill in client name, amount, billing period, and description.
4. Submit. Status becomes `PENDING`.

### 2. Accounts — Review & Approve/Reject
1. Log in as an Accounts user.
2. Open the **Review Queue** to see all `PENDING` requests.
3. Open a request, review details, add a note.
4. Click **Approve** (status → `APPROVED`, invoice auto-generated) or **Reject** (status → `REJECTED`).
5. All actions append to the **Audit Trail**.

### 3. Management — Dashboard Overview
1. Log in as a Management user.
2. See summary metrics: total pending, total approved this month, total invoiced value.
3. Browse all invoices; view individual invoice details.

---

## Demo Credentials

| Role       | Email                        | Password   |
|------------|------------------------------|------------|
| Sales      | sales@fgl.demo               | demo1234   |
| Accounts   | accounts@fgl.demo            | demo1234   |
| Management | management@fgl.demo          | demo1234   |

> Roles are seeded automatically on first run.

---

## How to Run

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Troublesome12/fgl-erp-workflow
cd fgl-erp-workflow

# 2. Copy env file
cp .env.example .env

# 3. Build and start
docker compose up --build

# 4. Open in your browser
# App:  http://localhost:3000
# API:  http://localhost:8000/docs  (OpenAPI / Swagger UI)
```

> **Fully self-contained.** No external services or API keys required.

> If you previously ran the FastAPI version, reset the database first:
> `docker compose down -v` then `docker compose up --build`

### Stopping

```bash
docker compose down          # Stop containers
docker compose down -v       # Stop and remove database volume
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                 │
│                                                 │
│  ┌──────────────┐     ┌──────────────────────┐  │
│  │   Frontend   │────▶│   Backend API        │  │
│  │  React/Vite  │     │   Django REST API    │  │
│  │  Port: 3000  │     │   Port: 8000         │  │
│  └──────────────┘     └──────────┬───────────┘  │
│                                  │              │
│                       ┌──────────▼───────────┐  │
│                       │   PostgreSQL 16      │  │
│                       │   Port: 5432         │  │
│                       └──────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Stack

| Layer       | Technology                                  |
|-------------|---------------------------------------------|
| Backend     | Python 3.12, Django 5, Django REST Framework |
| Frontend    | React 18, Vite, TailwindCSS, React Query    |
| Database    | PostgreSQL 16                               |
| Auth        | JWT via djangorestframework-simplejwt         |
| Deployment  | Docker Compose                              |

### Service Boundaries

- **`/api/auth`** — Login, JWT issue.
- **`/api/requests`** — CRUD for billing requests (Sales role).
- **`/api/reviews`** — Approve/reject actions (Accounts role).
- **`/api/invoices`** — Invoice listing and detail (Management role).
- **`/api/audit`** — Read-only audit trail per request.

---

## Data Model Overview

```
User
  id, email, hashed_password, role (SALES | ACCOUNTS | MANAGEMENT), created_at

BillingRequest
  id, created_by (→ User), client_name, amount, billing_period, description
  status (PENDING | APPROVED | REJECTED), created_at, updated_at

ReviewNote
  id, request_id (→ BillingRequest), reviewed_by (→ User)
  decision (APPROVED | REJECTED), note, reviewed_at

Invoice
  id, request_id (→ BillingRequest), invoice_number (auto-generated)
  amount, issued_at, status (ISSUED | PAID)

AuditLog
  id, entity_type, entity_id, actor_id (→ User), action, detail, timestamp
```

**Key decisions:**
- `AuditLog` is append-only and never deleted — every status change and review action is logged.
- `Invoice` is auto-created when a `BillingRequest` moves to `APPROVED` — no separate creation step needed.
- Roles are stored on `User` and enforced via DRF permission classes on every route.

---

## Testing Approach

```bash
# Run backend tests
docker compose exec backend pytest tests/ -v

# Run with coverage
docker compose exec backend pytest tests/ --cov=workflow --cov-report=term-missing
```

**Test coverage:**
- Unit tests for workflow state machine (valid/invalid transitions).
- Integration tests for key API routes: create request, approve, reject, invoice generation.
- Auth middleware tested for role enforcement (403 on wrong role).

---

## Test Overview

The backend tests are written using `pytest` and `pytest-django`, located in the `backend/tests/` directory. The testing strategy covers unit, integration, and authentication role enforcement.

### Structure & Coverage:

-   **`conftest.py`**: Contains shared fixtures, such as `api_client` for making API requests and `seeded_db` to ensure a consistent database state with predefined users and requests for tests.
-   **`test_workflow.py`**: Focuses on unit testing the core workflow state machine logic in `workflow/services/workflow.py`, ensuring correct transitions between request statuses (`PENDING`, `APPROVED`, `REJECTED`) and atomic invoice creation.
-   **`test_api_requests.py`**: Contains integration tests for the `/api/requests` endpoints, validating CRUD operations for billing requests and ensuring proper data serialization and deserialization.
-   **`test_audit.py`**: Verifies that all significant workflow actions (request creation, approval, rejection, invoice issuance) are correctly logged in the `AuditLog`.
-   **`test_auth.py`**: Tests authentication endpoints (`/api/auth/login`) and, crucially, validates the role-based permission system (`workflow/permissions.py`) by asserting that users with incorrect roles receive `403 Forbidden` responses when attempting unauthorized actions.

Tests are designed to be run in a Dockerized environment, replicating production conditions. The `login` helper function in `conftest.py` simplifies obtaining and setting JWT tokens for authenticated test requests.

## Known Limitations

- Authentication is simplified (no refresh tokens, no password reset). Not production-ready.
- No file attachment support (mentioned as a creative extension).
- No email/push notifications — audit log is the notification mechanism.
- Single-tenant only — no org/company isolation.

---

## What I Would Improve With More Time

- **Attachment support** — allow PDF/image uploads on billing requests (S3 or local volume).
- **Approval rules engine** — e.g., amounts above 1M BDT require dual sign-off.
- **Exportable reports** — CSV/PDF export of approved invoices by date range.
- **Notifications** — email simulation via a local SMTP container (Mailhog).
- **Production auth** — refresh tokens, rate limiting, proper password policies.
- **Frontend E2E tests** — Playwright or Cypress for the full workflow.

---

## AI Tools Used

| Tool              | How Used                                                              |
|-------------------|-----------------------------------------------------------------------|
| Claude (claude.ai)| Architecture design, context planning, code review, README drafting  |
| Google Gemini     | Boilerplate scaffolding, inline code suggestions, debugging           |

**Review process:** All AI-generated code was read line-by-line, tested locally, and adjusted where logic was incorrect or patterns didn't match the project's conventions. I take full ownership of everything submitted. AI was used as a productivity multiplier, not a replacement for engineering judgment.

---

## Repository Structure

```
fgl-erp-workflow/
├── backend/
│   ├── config/           # Django settings, URLs, WSGI
│   ├── workflow/         # Main app: models, views, serializers, services
│   ├── tests/
│   ├── manage.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── api/
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Design Notes & Tradeoffs

> See also [DESIGN.md](./DESIGN.md) for the full architecture note submitted with this assessment.

**Why Django REST Framework + React?**
Django REST Framework provides a mature, batteries-included API layer with serializers, permissions, and browsable docs. OpenAPI schema is available at `/docs` via drf-spectacular. React with React Query handles UI state, loading/error/empty patterns, and role-based routing on the frontend.

**Why PostgreSQL over SQLite?**
The audit log is append-heavy and the workflow involves concurrent role actions. PostgreSQL's row-level locking prevents double-approve race conditions with minimal effort. SQLite would have worked for a demo but felt like the wrong tradeoff signal.

**Mocked vs. real auth:**
Auth is JWT-based (SimpleJWT) but simplified — no refresh tokens, no email verification. The assessment note explicitly says "simple mocked users/roles are fine." Role enforcement via DRF permission classes is real and tested; the auth ceremony around it is deliberately minimal.
