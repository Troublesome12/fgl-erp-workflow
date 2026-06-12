/**
 * A simple loading state component that displays a spinner and an optional message.
 * @param message The message to display alongside the spinner. Defaults to "Loading...".
 */
export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex items-center justify-center py-16 text-slate-500">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      <span className="ml-3">{message}</span>
    </div>
  );
}
