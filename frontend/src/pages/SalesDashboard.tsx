import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchMyRequests } from "../api";
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
 * The SalesDashboard component displays a list of billing requests created by the logged-in sales user.
 * It allows sales users to view the status of their requests and navigate to create new ones or view request details.
 * It integrates with React Query to fetch and manage the state of billing requests.
 */
export function SalesDashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["my-requests"],
    queryFn: fetchMyRequests,
  });

  const nav = (
    <nav className="flex gap-4 text-sm">
      <Link to="/sales" className="font-medium text-brand-600">
        My Requests
      </Link>
      <Link to="/sales/new" className="text-slate-600 hover:text-brand-600">
        New Request
      </Link>
    </nav>
  );

  return (
    <Layout title="My Billing Requests" nav={nav}>
      <div className="mb-4 flex justify-end">
        <Link
          to="/sales/new"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          + New Request
        </Link>
      </div>

      {isLoading && <LoadingState />}
      {isError && <ErrorState message="Failed to load requests." />}
      {data && data.length === 0 && (
        <EmptyState message="No billing requests yet. Create your first one." />
      )}
      {data && data.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
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
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {data.map((req) => (
                <tr key={req.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <Link to={`/requests/${req.id}`} className="font-medium text-brand-600 hover:underline">
                      {req.client_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{req.billing_period}</td>
                  <td className="px-4 py-3 text-sm">{formatAmount(req.amount)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={req.status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500">
                    {new Date(req.created_at).toLocaleDateString()}
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
