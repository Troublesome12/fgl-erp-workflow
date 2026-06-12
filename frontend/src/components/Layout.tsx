import { Link, useNavigate } from "react-router-dom";
import { clearAuth, getStoredEmail } from "../api/client";

/**
 * Props for the Layout component.
 */
interface LayoutProps {
  /** The content to be rendered within the main section of the layout. */
  children: React.ReactNode;
  /** The title displayed prominently at the top of the main content area. */
  title: string;
  /** Optional navigation elements to be displayed in the header. */
  nav?: React.ReactNode;
}

/**
 * A responsive and consistent layout component that includes a header with dynamic navigation,
 * user email, and a logout button, along with a main content area for pages.
 * It provides a consistent visual structure across the application.
 */
export function Layout({ children, title, nav }: LayoutProps) {
  const navigate = useNavigate();
  const email = getStoredEmail();

  function handleLogout() {
    clearAuth();
    navigate("/login");
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-lg font-semibold text-brand-700">
              FGL ERP
            </Link>
            {nav}
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-600">
            <span>{email}</span>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md border border-slate-300 px-3 py-1.5 hover:bg-slate-50"
            >
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-bold text-slate-900">{title}</h1>
        {children}
      </main>
    </div>
  );
}
