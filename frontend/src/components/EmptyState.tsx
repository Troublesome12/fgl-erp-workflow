/**
 * A component to display a message when there is no data to show.
 * It provides a visually distinct way to inform the user about empty states.
 * @param message The message to display in the empty state.
 */
export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-slate-500">
      {message}
    </div>
  );
}
