import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchPendingRequests } from "../api";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { Layout } from "../components/Layout";
import { LoadingState } from "../components/LoadingState";

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
 * The ReviewQueue component displays a list of pending billing requests for Accounts users.
 * It allows them to view requests in a card format, showing key details and status.
 * Clicking on a request navigates to the RequestDetail page for review.
 * It uses React Query to fetch and manage the state of pending requests.
 */
export function ReviewQueue() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["pending-requests"],
    queryFn: fetchPendingRequests,
  });

  const nav = (
    <nav className="flex gap-4 text-sm">
      <Link to="/review" className="font-medium text-brand-600">
        Review Queue
      </Link>
    </nav>
  );

  return (
    <Layout title="Review Queue" nav={nav}>
      {isLoading && <LoadingState />}
      {isError && <ErrorState message="Failed to load pending requests." />}
      {data && data.length === 0 && (
        <EmptyState message="No pending requests — all caught up!" />
      )}
      {data && data.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {data.map((req) => (
            <Link
              key={req.id}
              to={`/requests/${req.id}`}
              className="block rounded-lg border border-slate-200 bg-white p-5 transition hover:border-brand-300 hover:shadow-sm"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-slate-900">{req.client_name}</h3>
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                  PENDING
                </span>
              </div>
              <p className="mt-2 text-lg font-medium text-brand-700">{formatAmount(req.amount)}</p>
              <p className="mt-1 text-sm text-slate-600">{req.billing_period}</p>
              <p className="mt-2 line-clamp-2 text-sm text-slate-500">{req.description}</p>
              <p className="mt-3 text-xs text-slate-400">
                Submitted by {req.creator_email} · {new Date(req.created_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      )}
    </Layout>
  );
}
