import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { approveRequest, fetchRequest, rejectRequest } from "../api";
import { getStoredRole } from "../api/client";
import { AuditTrail } from "../components/AuditTrail";
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
 * The RequestDetail component displays the full details of a single billing request.
 * It shows client information, amount, description, status, related invoice (if any), and review notes.
 * Accounts users can also approve or reject requests directly from this page.
 * It fetches data using React Query and includes an AuditTrail component.
 */
export function RequestDetail() {
  const { id } = useParams<{ id: string }>();
  const requestId = Number(id);
  const role = getStoredRole();
  const queryClient = useQueryClient();
  const [note, setNote] = useState("");
  const [actionError, setActionError] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["request", requestId],
    queryFn: () => fetchRequest(requestId),
    enabled: !Number.isNaN(requestId),
  });

  const approveMutation = useMutation({
    mutationFn: () => approveRequest(requestId, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["request", requestId] });
      queryClient.invalidateQueries({ queryKey: ["pending-requests"] });
      queryClient.invalidateQueries({ queryKey: ["my-requests"] });
      setNote("");
    },
    onError: () => setActionError("Failed to approve request."),
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectRequest(requestId, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["request", requestId] });
      queryClient.invalidateQueries({ queryKey: ["pending-requests"] });
      queryClient.invalidateQueries({ queryKey: ["my-requests"] });
      setNote("");
    },
    onError: () => setActionError("Failed to reject request."),
  });

  function handleAction(e: FormEvent, action: "approve" | "reject") {
    e.preventDefault();
    setActionError("");
    if (!note.trim()) {
      setActionError("Please add a review note.");
      return;
    }
    if (action === "approve") approveMutation.mutate();
    else rejectMutation.mutate();
  }

  const backPath = role === "ACCOUNTS" ? "/review" : "/sales";

  if (isLoading) {
    return (
      <Layout title="Request Detail">
        <LoadingState />
      </Layout>
    );
  }

  if (isError || !data) {
    return (
      <Layout title="Request Detail">
        <ErrorState message="Request not found or access denied." />
        <Link to={backPath} className="mt-4 inline-block text-brand-600 hover:underline">
          ← Go back
        </Link>
      </Layout>
    );
  }

  const canReview = role === "ACCOUNTS" && data.status === "PENDING";

  return (
    <Layout title={`Request #${data.id}`}>
      <Link to={backPath} className="mb-4 inline-block text-sm text-brand-600 hover:underline">
        ← Back
      </Link>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold">{data.client_name}</h2>
            <p className="mt-1 text-sm text-slate-500">
              {data.billing_period} · Submitted by {data.creator_email}
            </p>
          </div>
          <StatusBadge status={data.status} />
        </div>

        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-slate-500">Amount</dt>
            <dd className="text-lg font-semibold">{formatAmount(data.amount)}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500">Created</dt>
            <dd>{new Date(data.created_at).toLocaleString()}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm text-slate-500">Description</dt>
            <dd className="mt-1">{data.description}</dd>
          </div>
        </dl>

        {data.invoice && (
          <div className="mt-6 rounded-lg bg-blue-50 p-4">
            <p className="text-sm font-medium text-blue-800">
              Invoice {data.invoice.invoice_number} issued — {formatAmount(data.invoice.amount)}
            </p>
          </div>
        )}

        {data.review_notes.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-slate-700">Review Notes</h3>
            <ul className="mt-2 space-y-2">
              {data.review_notes.map((n) => (
                <li key={n.id} className="rounded border border-slate-200 p-3 text-sm">
                  <span className="font-medium">{n.decision}</span> by {n.reviewer_email}
                  <p className="mt-1 text-slate-600">{n.note}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {canReview && (
          <form className="mt-6 border-t border-slate-200 pt-6">
            <label htmlFor="note" className="block text-sm font-medium text-slate-700">
              Review Note
            </label>
            <textarea
              id="note"
              rows={3}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              placeholder="Add your review comments..."
            />
            {actionError && <p className="mt-2 text-sm text-red-600">{actionError}</p>}
            <div className="mt-3 flex gap-3">
              <button
                type="button"
                onClick={(e) => handleAction(e, "approve")}
                disabled={approveMutation.isPending || rejectMutation.isPending}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                Approve
              </button>
              <button
                type="button"
                onClick={(e) => handleAction(e, "reject")}
                disabled={approveMutation.isPending || rejectMutation.isPending}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
            </div>
          </form>
        )}
      </div>

      <AuditTrail entityType="BillingRequest" entityId={data.id} />
    </Layout>
  );
}
