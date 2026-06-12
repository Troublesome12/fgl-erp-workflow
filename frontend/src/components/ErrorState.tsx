/**
 * A component to display an error message in a styled box.
 * @param message The error message to display.
 */
export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-6 text-center text-red-700">
      {message}
    </div>
  );
}
