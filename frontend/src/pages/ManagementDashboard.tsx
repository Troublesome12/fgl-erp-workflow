import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchInvoiceMetrics, fetchInvoices } from "../api";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { Layout } from "../components/Layout";
import { LoadingState } from "../components/LoadingState";
import { StatusBadge } from "../components/StatusBadge";

/**
 * Formats a numeric amount into a currency string in BDT.
 * @param amount The amount to format.
 * @returns The formatted currency string.
 */
function formatAmount(amount: string): string {
  return new Intl.NumberFormat("en-BD", { style: "currency", currency: "BDT" }).format(
    Number(amount),
  );
}

/**
 * Props for the MetricCard component.
 */
interface MetricCardProps {
  /** The label for the metric (e.g., "Total Invoiced Value"). */
  label: string;
  /** The value of the metric (can be a string or a number). */
  value: string | number;
}

/**
 * A simple card component to display a single metric with a label and value.
 * Used for summarizing key figures on the Management Dashboard.
 */
function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

/**
 * The ManagementDashboard component provides an overview for Management users.
 * It displays key financial metrics (pending requests, monthly approvals, total invoiced value, total invoices)
 * and a list of all issued invoices. It fetches data using React Query.
 */
export function ManagementDashboard() {
  const metricsQuery = useQuery({
    queryKey: ["invoice-metrics"],
    queryFn: fetchInvoiceMetrics,
  });

  const invoicesQuery = useQuery({
    queryKey: ["invoices"],
    queryFn: fetchInvoices,
  });

  const nav = (
    <nav className="flex gap-4 text-sm">
      <Link to="/management" className="font-medium text-brand-600">
        Dashboard
      </Link>
    </nav>
  );

  const isLoading = metricsQuery.isLoading || invoicesQuery.isLoading;
  const isError = metricsQuery.isError || invoicesQuery.isError;

  return (
    <Layout title="Management Dashboard" nav={nav}>
      {isLoading && <LoadingState />}
      {isError && <ErrorState message="Failed to load dashboard data." />}

      {metricsQuery.data && (
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Pending Requests" value={metricsQuery.data.total_pending} />
          <MetricCard
            label="Approved This Month"
            value={metricsQuery.data.total_approved_this_month}
          />
          <MetricCard
            label="Total Invoiced Value"
            value={formatAmount(metricsQuery.data.total_invoiced_value)}
          />
          <MetricCard label="Total Invoices" value={metricsQuery.data.total_invoices} />
        </div>
      )}

      <h2 className="mb-4 text-lg font-semibold">Invoices</h2>
      {invoicesQuery.data && invoicesQuery.data.length === 0 && (
        <EmptyState message="No invoices issued yet." />
      )}
      {invoicesQuery.data && invoicesQuery.data.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Invoice #
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Client
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Period
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-slate-500">
                  Issued
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {invoicesQuery.data.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-brand-600">{inv.invoice_number}</td>
                  <td className="px-4 py-3">{inv.client_name}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{inv.billing_period}</td>
                  <td className="px-4 py-3">{formatAmount(inv.amount)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={inv.status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {new Date(inv.issued_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Layout>
  );
}
