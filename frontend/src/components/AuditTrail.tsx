import { useQuery } from "@tanstack/react-query";
import { fetchAuditTrail } from "../api";
import { ErrorState } from "./ErrorState";
import { LoadingState } from "./LoadingState";

/**
 * Props for the AuditTrail component.
 */
interface AuditTrailProps {
  /** The type of the entity for which to display the audit trail (e.g., "BillingRequest", "Invoice"). */
  entityType: string;
  /** The ID of the entity for which to display the audit trail. */
  entityId: number;
}

/**
 * A component that fetches and displays the audit trail for a specific entity.
 * It uses React Query to manage the data fetching and displays loading/error states.
 */
export function AuditTrail({ entityType, entityId }: AuditTrailProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["audit", entityType, entityId],
    queryFn: () => fetchAuditTrail(entityType, entityId),
  });

  if (isLoading) return <LoadingState message="Loading audit trail..." />;
  if (isError) return <ErrorState message="Could not load audit trail." />;
  if (!data?.length) return null;

  return (
    <div className="mt-8">
      <h3 className="mb-3 text-lg font-semibold">Audit Trail</h3>
      <ol className="space-y-3">
        {data.map((entry) => (
          <li key={entry.id} className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-brand-700">{entry.action}</span>
              <time className="text-slate-500">
                {new Date(entry.timestamp).toLocaleString()}
              </time>
            </div>
            <p className="mt-1 text-sm text-slate-700">{entry.detail}</p>
            {entry.actor_email && (
              <p className="mt-1 text-xs text-slate-500">by {entry.actor_email}</p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
