# Design Notes — FGL ERP Workflow Module

## Problem

Internal teams at FGL coordinate billing manually between Sales, Accounts, and Management. Requests get lost in email threads, approvals lack audit trails, and invoices are created inconsistently after approval.

## Solution

A focused **Sales → Accounts → Management** billing workflow:

1. Sales raises a billing request (client, amount, period, description).
2. Accounts reviews pending requests and approves or rejects with a mandatory note.
3. On approval, an invoice is auto-generated atomically in the same transaction.
4. Management views summary metrics and all issued invoices.

Every state change is recorded in an append-only audit log.

## Architecture Decisions

### Django REST Framework + React split

- Backend exposes a REST API with OpenAPI docs at `/docs` (drf-spectacular).
- Frontend is a SPA served by nginx, proxying `/api` to the backend container.
- Business logic lives in `workflow/services/workflow.py`, not views.

### PostgreSQL

Chosen over SQLite because the workflow involves concurrent approve actions. `SELECT ... FOR UPDATE` prevents double-approval race conditions.

### JWT auth with role enforcement

Simple JWT login with role claims. Every protected route uses `require_role()` dependency injection. Auth ceremony is minimal per assessment guidance; enforcement logic is real and tested.

### Atomic invoice creation

Approve + invoice creation + audit logs happen in one DB transaction. If invoice creation fails, the approval rolls back.

## Tradeoffs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Auth | JWT, no refresh tokens | Session cookies | Faster to build; sufficient for demo |
| Notifications | Audit log only | Email via Mailhog | Out of scope; audit log demonstrates traceability |
| Multi-tenancy | Single tenant | Org isolation | Not needed for assessment scope |
| File attachments | None | S3/local uploads | Would add complexity without core workflow value |

## Assumptions

- All amounts are in BDT.
- One invoice per approved billing request.
- Accounts is the sole approver (no dual sign-off for large amounts).
- Management has read-only access to invoices and metrics.
- Seed data is idempotent — skipped if users already exist.

## Known Limitations

See README.md for full list. Primary gaps: no attachments, no notifications, no export, simplified auth.

## What I'd Improve Next

1. Approval rules engine (e.g., amounts > 1M BDT require Management co-sign).
2. CSV/PDF invoice export.
3. Simulated email notifications via Mailhog.
4. Playwright E2E tests for the full three-role flow.
