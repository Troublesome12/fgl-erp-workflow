import type { InvoiceStatus, RequestStatus } from "../types";

const statusStyles: Record<string, string> = {
  PENDING: "bg-amber-100 text-amber-800",
  APPROVED: "bg-green-100 text-green-800",
  REJECTED: "bg-red-100 text-red-800",
  ISSUED: "bg-blue-100 text-blue-800",
  PAID: "bg-emerald-100 text-emerald-800",
};

/**
 * Props for the StatusBadge component.
 */
interface StatusBadgeProps {
  /** The status string to display (e.g., "PENDING", "APPROVED", "ISSUED"). */
  status: RequestStatus | InvoiceStatus | string;
}

/**
 * A reusable UI component that displays a colored badge based on a given status string.
 * It automatically applies appropriate styling for different request and invoice statuses.
 */
export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[status] ?? "bg-slate-100 text-slate-700"}`}
    >
      {status}
    </span>
  );
}
