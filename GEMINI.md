# GEMINI.md — Project Context for AI Coding Assistant

> This file provides full project context so Gemini can assist effectively.
> Keep this file open or paste it at the start of any Gemini session before asking for code help.

---

## Project Summary

**Project:** FGL Lead Full-Stack Engineer Take-Home Assessment — Option 1: ERP Workflow Module
**Developer:** Arafat (Senior Software Engineer / Backend Team Lead)
**Deadline:** Sunday, 14 June 2026 at 09:00 AM (Asia/Dhaka)
**Repo:** https://github.com/Troublesome12/fgl-erp-workflow

A small internal ERP system for a **Sales → Accounts → Management** billing approval workflow. The goal is clean architecture, real role-based access, a sensible data model, and a fully auditable workflow — not a large system.

---

## Tech Stack

| Layer      | Technology                                        |
|------------|---------------------------------------------------|
| Backend    | Python 3.12, Django 5, Django REST Framework      |
| Frontend   | React 18, Vite, TailwindCSS, React Query v5       |
| Database   | PostgreSQL 16                                     |
| Auth       | JWT via djangorestframework-simplejwt             |
| Containers | Docker + Docker Compose                           |
| Testing    | pytest + pytest-django (backend)                  |

---

## Repository Structure

```
fgl-erp-workflow/
├── backend/
│   ├── config/
│   │   ├── settings.py         # Django settings
│   │   ├── urls.py             # Root URL config + /docs
│   │   └── wsgi.py
│   ├── workflow/
│   │   ├── models.py           # Django ORM models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API views (auth, requests, reviews, invoices, audit)
│   │   ├── urls.py             # /api/* routes
│   │   ├── permissions.py      # Role-based permission classes
│   │   ├── services/
│   │   │   └── workflow.py     # State machine + invoice auto-creation
│   │   ├── management/commands/
│   │   │   └── seed_data.py    # Seed users and sample requests
│   │   └── migrations/
│   ├── tests/
│   │   ├── test_workflow.py
│   │   ├── test_api_requests.py
│   │   └── test_auth.py
│   ├── manage.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Shared UI components
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── SalesDashboard.tsx
│   │   │   ├── NewRequest.tsx
│   │   │   ├── ReviewQueue.tsx
│   │   │   ├── RequestDetail.tsx
│   │   │   └── ManagementDashboard.tsx
│   │   ├── hooks/              # React Query hooks per entity
│   │   └── api/                # Axios API client + typed functions
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── package.json
├── docker-compose.yml
├── .env.example
├── README.md
└── GEMINI.md
```

---

## Data Models

### Django Models (`backend/workflow/models.py`)

```python
class UserRole(str, Enum):
    SALES = "SALES"
    ACCOUNTS = "ACCOUNTS"
    MANAGEMENT = "MANAGEMENT"

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class InvoiceStatus(str, Enum):
    ISSUED = "ISSUED"
    PAID = "PAID"

class User(Base):
    __tablename__ = "users"
    id: int (PK)
    email: str (unique)
    hashed_password: str
    role: UserRole
    created_at: datetime

class BillingRequest(Base):
    __tablename__ = "billing_requests"
    id: int (PK)
    created_by: int (FK → users.id)
    client_name: str
    amount: Decimal(10,2)
    billing_period: str        # e.g. "June 2026"
    description: str
    status: RequestStatus      # default PENDING
    created_at: datetime
    updated_at: datetime

class ReviewNote(Base):
    __tablename__ = "review_notes"
    id: int (PK)
    request_id: int (FK → billing_requests.id)
    reviewed_by: int (FK → users.id)
    decision: str              # "APPROVED" | "REJECTED"
    note: str
    reviewed_at: datetime

class Invoice(Base):
    __tablename__ = "invoices"
    id: int (PK)
    request_id: int (FK → billing_requests.id, unique)
    invoice_number: str        # auto-generated, e.g. "INV-2026-0001"
    amount: Decimal(10,2)
    issued_at: datetime
    status: InvoiceStatus      # default ISSUED

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: int (PK)
    entity_type: str           # "BillingRequest" | "Invoice"
    entity_id: int
    actor_id: int (FK → users.id)
    action: str                # "CREATED" | "APPROVED" | "REJECTED" | "INVOICE_ISSUED"
    detail: str                # human-readable description
    timestamp: datetime
```

---

## API Endpoints

### Auth
| Method | Path              | Role | Description             |
|--------|-------------------|------|-------------------------|
| POST   | /api/auth/login   | Any  | Returns JWT access token |

### Billing Requests
| Method | Path                     | Role     | Description                        |
|--------|--------------------------|----------|------------------------------------|
| GET    | /api/requests            | SALES    | List own requests                  |
| POST   | /api/requests            | SALES    | Create new billing request         |
| GET    | /api/requests/{id}       | SALES, ACCOUNTS | Get request detail          |
| GET    | /api/requests/pending    | ACCOUNTS | List all PENDING requests          |

### Reviews
| Method | Path                     | Role     | Description                        |
|--------|--------------------------|----------|------------------------------------|
| POST   | /api/reviews/{request_id}/approve | ACCOUNTS | Approve + auto-create invoice |
| POST   | /api/reviews/{request_id}/reject  | ACCOUNTS | Reject with note             |

### Invoices
| Method | Path                     | Role       | Description              |
|--------|--------------------------|------------|--------------------------|
| GET    | /api/invoices            | MANAGEMENT | List all invoices        |
| GET    | /api/invoices/{id}       | MANAGEMENT | Invoice detail           |
| GET    | /api/invoices/metrics    | MANAGEMENT | Summary counts + totals  |

### Audit
| Method | Path                         | Role  | Description                    |
|--------|------------------------------|-------|--------------------------------|
| GET    | /api/audit/{entity_type}/{id}| Any   | Audit trail for a given entity |

---

## Workflow State Machine

```
[New Request]
     │
     ▼
  PENDING  ──── (Accounts: Reject) ──▶  REJECTED
     │
     │ (Accounts: Approve)
     ▼
  APPROVED  ──────────────────────────▶  Invoice auto-created (ISSUED)
```

**Rules enforced in `workflow/services/workflow.py`:**
- Only `ACCOUNTS` role can approve or reject.
- A `PENDING` request can only be approved or rejected (no other transitions).
- Approving a request triggers atomic invoice creation in the same DB transaction.
- All transitions write to `AuditLog`.

---

## Auth & Role Enforcement

JWT is issued on login via `LoginView` + SimpleJWT. Every protected view uses DRF permission classes:

```python
# workflow/permissions.py
def role_permission(*roles: UserRole) -> type[HasRole]:
    class _RolePermission(HasRole):
        allowed_roles = tuple(r.value for r in roles)
    return _RolePermission

# Usage in view
class ReviewApproveView(APIView):
    permission_classes = [role_permission(UserRole.ACCOUNTS)]
    ...
```

---

## Seed Data (`workflow/management/commands/seed_data.py`)

On first run, the following is seeded:

**Users:**
- `sales@fgl.demo` / `demo1234` → SALES
- `accounts@fgl.demo` / `demo1234` → ACCOUNTS
- `management@fgl.demo` / `demo1234` → MANAGEMENT

**Billing Requests (mix of statuses for demo purposes):**
- 3 × PENDING
- 2 × APPROVED (with invoices)
- 1 × REJECTED

---

## Docker Compose

```yaml
# docker-compose.yml (summary)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: fgl_erp
      POSTGRES_USER: fgl
      POSTGRES_PASSWORD: fglpass
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      POSTGRES_DB: fgl_erp
      POSTGRES_USER: fgl
      POSTGRES_PASSWORD: fglpass
      POSTGRES_HOST: db
      SECRET_KEY: dev-secret-key

  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [backend]

volumes:
  pgdata:
```

---

## Environment Variables (`.env.example`)

```
POSTGRES_DB=fgl_erp
POSTGRES_USER=fgl
POSTGRES_PASSWORD=fglpass
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

---

## Coding Conventions

### Backend
- Use Django ORM with `transaction.atomic()` for workflow actions.
- Keep business logic in `workflow/services/`, not in views.
- Views only: validate input via serializers → call service → return response.
- Invoice creation and status update must be atomic (same transaction).
- Use DRF `ValidationError`, `PermissionDenied`, `NotFound` for errors.
- Never expose `password` in any serializer response.

### Frontend
- TypeScript throughout.
- Use **React Query** (`useQuery`, `useMutation`) for all API calls — no raw `useEffect` for data fetching.
- Axios instance in `api/client.ts` with JWT interceptor.
- Every page must handle: loading state, error state, empty state.
- TailwindCSS only — no additional CSS frameworks.
- Role-based routing: redirect to correct dashboard after login based on JWT role claim.

### General
- No `any` in TypeScript.
- No print/console.log left in production paths — use Python `logging` and browser `console.error` only for genuine errors.
- Keep components small and focused — split if a component exceeds ~150 lines.

---

## What's Out of Scope

- Email/push notifications (audit log serves this purpose for the demo).
- File attachments.
- Multi-tenancy.
- Password reset / refresh tokens.
- Payment processing.

Do not add these unless explicitly asked.

---

## Prompt Tips for This Project

When asking Gemini for help, be specific about the layer:

- **"Write the SQLAlchemy model for..."** → reference the models section above.
- **"Write the FastAPI route for approving a billing request"** → reference the workflow rules and auth pattern.
- **"Write the React Query hook for fetching pending requests"** → mention the endpoint, expected response shape, and TypeScript type.
- **"Write a pytest test for..."** → mention the route, the role required, and the expected behaviour.

Always ask Gemini to follow the conventions section above.
