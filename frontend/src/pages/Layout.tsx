import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ArrowLeftRight,
  Search,
  ShieldAlert,
  FolderOpen,
  Link2,
  MessageCircleHeart,
  FileBarChart,
  Settings2,
  LogOut,
  Radio,
} from "lucide-react";
import { Logo } from "@/components/Logo";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";

const NAV = [
  { to: "/", label: "Command Center", icon: LayoutDashboard },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { to: "/investigate", label: "Investigate", icon: Search },
  { to: "/flagged", label: "Flagged Accounts", icon: ShieldAlert },
  { to: "/cases", label: "Cases", icon: FolderOpen },
  { to: "/link-analyzer", label: "Link Analyzer", icon: Link2 },
  { to: "/victim-chat", label: "Victim Assistant", icon: MessageCircleHeart },
  { to: "/reports", label: "Reports", icon: FileBarChart },
  { to: "/admin", label: "System Admin", icon: Settings2 },
];

export function Layout() {
  const { user, token, signOut } = useAuth();
  const navigate = useNavigate();
  const [clock, setClock] = useState(new Date());
  const [sim, setSim] = useState<any>(null);

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    api
      .get<any>("/simulator/status", token)
      .then(setSim)
      .catch(() => {});
    const t = setInterval(() => {
      api
        .get<any>("/simulator/status", token)
        .then(setSim)
        .catch(() => {});
    }, 15000);
    return () => clearInterval(t);
  }, [token]);

  const onLogout = async () => {
    await signOut();
    navigate("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="flex w-60 shrink-0 flex-col border-r border-cyber-cyan/10 bg-ink-900/80 backdrop-blur">
        <div className="border-b border-cyber-cyan/10 px-5 py-5">
          <Logo />
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-200 ${
                  isActive
                    ? "bg-cyber-cyan/10 font-medium text-cyber-cyan"
                    : "text-slate-400 hover:bg-ink-800/70 hover:text-slate-200"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 h-6 w-0.5 -translate-y-1/2 rounded bg-cyber-cyan shadow-glow" />
                  )}
                  <Icon className="h-4 w-4" />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-cyber-cyan/10 px-4 py-4">
          <div className="mb-3 flex items-center gap-2 rounded-lg border border-cyber-cyan/10 bg-ink-850 px-3 py-2">
            <Radio
              className={`h-3.5 w-3.5 ${sim?.running ? "animate-pulse text-cyber-green" : "text-slate-500"}`}
            />
            <div className="font-mono text-[10px] text-slate-400">
              <div>{sim?.running ? "STREAMING LIVE" : "SIMULATOR IDLE"}</div>
              <div className="text-slate-500">
                {sim?.counts ? `${sim.counts.sent} txns · ${sim.counts.blocked} blocked` : "—"}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full border border-cyber-cyan/30 bg-cyber-cyan/10 font-display text-xs font-bold text-cyber-cyan">
              {(user?.email ?? "A").slice(0, 1).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium text-slate-200">{user?.email}</div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-cyber-cyan/60">
                Analyst
              </div>
            </div>
            <button
              onClick={onLogout}
              className="rounded p-1.5 text-slate-500 transition-colors hover:bg-cyber-red/10 hover:text-cyber-red"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-cyber-cyan/10 bg-ink-900/50 px-6 py-3 backdrop-blur">
          <div className="font-mono text-[11px] uppercase tracking-[0.25em] text-slate-500">
            AI Financial Fraud Detection · Prevention Platform
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden items-center gap-1.5 font-mono text-[11px] text-slate-400 md:flex">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyber-green" />
              ENGINE ONLINE
            </span>
            <span className="font-mono text-sm tabular-nums text-cyber-cyan/80">
              {clock.toLocaleTimeString("en-IN", { hour12: false })}
            </span>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}