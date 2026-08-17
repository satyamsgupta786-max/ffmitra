import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/hooks/useAuth";
import { Layout } from "@/pages/Layout";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import { Transactions } from "@/pages/Transactions";
import { Investigate } from "@/pages/Investigate";
import { FlaggedAccounts } from "@/pages/FlaggedAccounts";
import { Cases } from "@/pages/Cases";
import { LinkAnalyzer } from "@/pages/LinkAnalyzer";
import { VictimChat } from "@/pages/VictimChat";
import { Reports } from "@/pages/Reports";
import { Admin } from "@/pages/Admin";
import { Loader2 } from "lucide-react";

function Protected({ children }: { children: React.ReactNode }) {
  const { session, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-cyber-cyan" />
      </div>
    );
  }
  if (!session) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <Protected>
              <Layout />
            </Protected>
          }
        >
          <Route path="/" element={<Dashboard />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/investigate" element={<Investigate />} />
          <Route path="/flagged" element={<FlaggedAccounts />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/link-analyzer" element={<LinkAnalyzer />} />
          <Route path="/victim-chat" element={<VictimChat />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/admin" element={<Admin />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}