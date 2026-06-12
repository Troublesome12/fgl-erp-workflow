import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";
import { setAuthToken } from "../api/client";
import type { UserRole } from "../types";

const roleRoutes: Record<UserRole, string> = {
  SALES: "/sales",
  ACCOUNTS: "/review",
  MANAGEMENT: "/management",
};

/**
 * The Login page component handles user authentication.
 * It provides a form for users to enter their email and password, attempts to log them in,
 * and redirects them to the appropriate dashboard based on their role upon successful authentication.
 * It also displays demo credentials for easy testing.
 */
export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("sales@fgl.demo");
  const [password, setPassword] = useState("demo1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(email, password);
      setAuthToken(data.access_token, data.role, data.email);
      navigate(roleRoutes[data.role]);
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-900 to-brand-700 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-slate-900">FGL ERP Workflow</h1>
        <p className="mt-1 text-sm text-slate-500">Sales → Accounts → Management</p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-brand-600 py-2.5 font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-6 rounded-lg bg-slate-50 p-4 text-xs text-slate-600">
          <p className="font-medium">Demo accounts (password: demo1234)</p>
          <ul className="mt-2 space-y-1">
            <li>sales@fgl.demo — Sales</li>
            <li>accounts@fgl.demo — Accounts</li>
            <li>management@fgl.demo — Management</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
