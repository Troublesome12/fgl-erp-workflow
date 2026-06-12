import { apiClient } from "./client";
import type {
  AuditLog,
  BillingRequest,
  BillingRequestDetail,
  CreateRequestPayload,
  Invoice,
  InvoiceMetrics,
  TokenResponse,
} from "../types";

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function fetchMyRequests(): Promise<BillingRequest[]> {
  const { data } = await apiClient.get<BillingRequest[]>("/requests");
  return data;
}

export async function fetchPendingRequests(): Promise<BillingRequest[]> {
  const { data } = await apiClient.get<BillingRequest[]>("/requests/pending");
  return data;
}

export async function fetchRequest(id: number): Promise<BillingRequestDetail> {
  const { data } = await apiClient.get<BillingRequestDetail>(`/requests/${id}`);
  return data;
}

export async function createRequest(payload: CreateRequestPayload): Promise<BillingRequest> {
  const { data } = await apiClient.post<BillingRequest>("/requests", payload);
  return data;
}

export async function approveRequest(id: number, note: string): Promise<BillingRequest> {
  const { data } = await apiClient.post<BillingRequest>(`/reviews/${id}/approve`, { note });
  return data;
}

export async function rejectRequest(id: number, note: string): Promise<BillingRequest> {
  const { data } = await apiClient.post<BillingRequest>(`/reviews/${id}/reject`, { note });
  return data;
}

export async function fetchInvoices(): Promise<Invoice[]> {
  const { data } = await apiClient.get<Invoice[]>("/invoices");
  return data;
}

export async function fetchInvoice(id: number): Promise<Invoice> {
  const { data } = await apiClient.get<Invoice>(`/invoices/${id}`);
  return data;
}

export async function fetchInvoiceMetrics(): Promise<InvoiceMetrics> {
  const { data } = await apiClient.get<InvoiceMetrics>("/invoices/metrics");
  return data;
}

export async function fetchAuditTrail(entityType: string, entityId: number): Promise<AuditLog[]> {
  const { data } = await apiClient.get<AuditLog[]>(`/audit/${entityType}/${entityId}`);
  return data;
}
