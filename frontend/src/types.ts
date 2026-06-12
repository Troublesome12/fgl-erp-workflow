/**
 * Represents the possible roles a user can have within the system.
 */
export type UserRole = "SALES" | "ACCOUNTS" | "MANAGEMENT";

/**
 * Represents the possible statuses for a billing request.
 */
export type RequestStatus = "PENDING" | "APPROVED" | "REJECTED";

/**
 * Represents the possible statuses for an invoice.
 */
export type InvoiceStatus = "ISSUED" | "PAID";

/**
 * Represents the response received after successful user login.
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  email: string;
}

/**
 * Represents a billing request made by a sales user.
 */
export interface BillingRequest {
  id: number;
  created_by: number; // FK to User
  client_name: string;
  amount: string; // Decimal is represented as string in JSON
  billing_period: string;
  description: string;
  status: RequestStatus;
  created_at: string;
  updated_at: string;
  creator_email?: string;
}

/**
 * Represents a review note made by an accounts user for a billing request.
 */
export interface ReviewNote {
  id: number;
  request_id: number; // FK to BillingRequest
  reviewed_by: number; // FK to User
  decision: string; // "APPROVED" | "REJECTED"
  note: string;
  reviewed_at: string;
  reviewer_email?: string;
}

/**
 * Represents an invoice generated after a billing request is approved.
 */
export interface Invoice {
  id: number;
  request_id: number; // FK to BillingRequest (unique)
  invoice_number: string;
  amount: string; // Decimal is represented as string in JSON
  issued_at: string;
  status: InvoiceStatus;
  client_name?: string;
  billing_period?: string;
}

/**
 * Represents a detailed billing request, including its review notes and associated invoice.
 */
export interface BillingRequestDetail extends BillingRequest {
  review_notes: ReviewNote[];
  invoice: Invoice | null;
}

/**
 * Represents summary metrics for invoices, typically for management dashboards.
 */
export interface InvoiceMetrics {
  total_pending: number;
  total_approved_this_month: number;
  total_invoiced_value: string;
  total_invoices: number;
}

/**
 * Represents an entry in the audit log, tracking changes to entities.
 */
export interface AuditLog {
  id: number;
  entity_type: string; // e.g., "BillingRequest" | "Invoice"
  entity_id: number;
  actor_id: number; // FK to User
  action: string; // e.g., "CREATED", "APPROVED", "REJECTED", "INVOICE_ISSUED"
  detail: string;
  timestamp: string;
  actor_email?: string;
}

/**
 * Represents the payload for creating a new billing request.
 */
export interface CreateRequestPayload {
  client_name: string;
  amount: string;
  billing_period: string;
  description: string;
}
