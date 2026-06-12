import { Navigate, Route, Routes } from "react-router-dom";
import { getStoredRole } from "./api/client";
import { Login } from "./pages/Login";
import { ManagementDashboard } from "./pages/ManagementDashboard";
import { NewRequest } from "./pages/NewRequest";
import { RequestDetail } from "./pages/RequestDetail";
import { ReviewQueue } from "./pages/ReviewQueue";
import { SalesDashboard } from "./pages/SalesDashboard";
import type { UserRole } from "./types";

function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles: UserRole[];
}) {
  const role = getStoredRole() as UserRole | null;
  if (!role) return <Navigate to="/login" replace />;
  if (!allowedRoles.includes(role)) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function HomeRedirect() {
  const role = getStoredRole() as UserRole | null;
  if (!role) return <Navigate to="/login" replace />;
  const routes: Record<UserRole, string> = {
    SALES: "/sales",
    ACCOUNTS: "/review",
    MANAGEMENT: "/management",
  };
  return <Navigate to={routes[role]} replace />;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<HomeRedirect />} />
      <Route
        path="/sales"
        element={
          <ProtectedRoute allowedRoles={["SALES"]}>
            <SalesDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/sales/new"
        element={
          <ProtectedRoute allowedRoles={["SALES"]}>
            <NewRequest />
          </ProtectedRoute>
        }
      />
      <Route
        path="/review"
        element={
          <ProtectedRoute allowedRoles={["ACCOUNTS"]}>
            <ReviewQueue />
          </ProtectedRoute>
        }
      />
      <Route
        path="/management"
        element={
          <ProtectedRoute allowedRoles={["MANAGEMENT"]}>
            <ManagementDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/requests/:id"
        element={
          <ProtectedRoute allowedRoles={["SALES", "ACCOUNTS", "MANAGEMENT"]}>
            <RequestDetail />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
