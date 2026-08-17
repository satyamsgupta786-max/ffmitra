import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Network, ShieldAlert, MapPin, Smartphone, GitBranch } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { FundTrailGraph } from "@/components/FundTrailGraph";
import { DecisionBadge } from "@/components/DecisionBadge";
import { fmtDateTime, fmtInr, shortRef } from "@/lib/utils";

export function Investigate() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const [trail, setTrail] = useState<any>(null);
  const [trailLoading, setTrailLoading] = useState(false);
  const [error, setError] = useState("");

  const loadProfile = useCallback(
    async (ref: string) => {
      setSearching(true);
      setError("");
      try {
        const data = await api.get<any>(`/investigate/account/${encodeURIComponent(ref)}`, token);
        setProfile(data);
      } catch (e: any) {
        setProfile(null);
        setError(e.message ?? "account not found");
      } finally {
        setSearching(false);
      }
    },
    [token]
  );

  const loadTrail = useCallback(
    async (ref: string) => {
      setTrailLoading(true);
      try {
        const data = await api.get<any>(`/investigate/fundtrail/${encodeURIComponent(ref)}?depth=2`, token);
        setTrail(data);
      } catch {
        setTrail(null);
      } finally {
        setTrailLoading(false);
      }
    },
    [token]
  );

  const run = async (ref?: string) => {
    const target = (ref ?? query).trim();
    if (!target) return;
    await loadProfile(target);
  };

  useEffect(() => {
    if (profile) loadTrail(profile.account.account_ref);
  }, [profile, loadTrail]);

  const p = profile;
  const s = p?.stats;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-display text-2xl font-bold text-slate-100">Investigate</h1>
        <p className="mt-0.5 font-mono text-xs text-slate-500">
          trace a Txn ID, UTR, account number, or UPI handle
        </p>
      </div>

      <div className="panel flex items-center gap-3 p-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="input pl-9"
            placeholder="e.g. UPI-000000000042 · ravi.kumar@okhdfc · mule.vendor@paytm · 9876543210@ybl"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()}
          />
        </div>
        <button className="btn-primary" onClick={() => run()} disabled={searching}>
          <Search className="h-4 w-4" />
          {searching ? "Tracing…" : "Trace"}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-cyber-red/30 bg-cyber-red/10 px-4 py-3 font-mono text-xs text-cyber-red">
          {error}
        </div>
      )}

      {p && (
        <>
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <div className="panel p-5 xl:col-span-2">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative flex h-11 w-11 items-center justify-center">
                    <span className="absolute inset-0 animate-pulse-ring rounded-full border border-cyber-cyan/50" />
                    <span className="relative flex h-9 w-9 items-center justify-center rounded-full border border-cyber-cyan/40 bg-cyber-cyan/10 font-display text-sm font-bold text-cyber-cyan">
                      {p.account.account_ref.slice(0, 1).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h2 className="font-mono text-sm font-semibold text-slate-100">{p.account.account_ref}</h2>
                    <div className="font-mono text-[11px] text-slate-500">
                      {p.account.account_type ?? "UNKNOWN"} · {p.account.bank ?? "UNKNOWN"}
                    </div>
                  </div>
                </div>
                {p.flagged ? (
                  <span className="chip border border-cyber-red/40 bg-cyber-red/10 text-cyber-red">
                    <ShieldAlert className="h-3 w-3" /> FLAGGED · {p.flagged.severity}
                  </span>
                ) : (
                  <span className="chip border border-cyber-green/30 bg-cyber-green/5 text-cyber-green">CLEAN</span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  ["Outgoing", s?.total_sent ?? 0, "#00E5FF"],
                  ["Incoming", s?.total_received ?? 0, "#7C5CFF"],
                  ["Transactions", s?.txn_count ?? 0, "#00FF9D"],
                  ["Devices", s?.devices?.length ?? 0, "#FFB020"],
                ].map(([label, value, color]) => (
                  <div key={label as string} className="rounded-lg border border-cyber-cyan/10 bg-ink-850 p-3">
                    <div className="font-mono text-[10px] uppercase tracking-wider text-slate-500">{label}</div>
                    <div className="mt-1 font-display text-lg font-bold tabular-nums" style={{ color: color as string }}>
                      {typeof value === "number" && (label === "Outgoing" || label === "Incoming") ? fmtInr(value) : value}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-cyber-cyan/10 bg-ink-850 p-3">
                  <div className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
                    <Smartphone className="h-3 w-3" /> Known Devices
                  </div>
                  {(s?.devices ?? []).length === 0 && <p className="font-mono text-[11px] text-slate-600">none recorded</p>}
                  {(s?.devices ?? []).map(([d, n]: [string, number]) => (
                    <div key={d} className="flex justify-between font-mono text-[11px] text-slate-300">
                      <span>{d}</span>
                      <span className="text-slate-500">×{n}</span>
                    </div>
                  ))}
                </div>
                <div className="rounded-lg border border-cyber-cyan/10 bg-ink-850 p-3">
                  <div className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
                    <MapPin className="h-3 w-3" /> Locations
                  </div>
                  {(s?.locations ?? []).length === 0 && <p className="font-mono text-[11px] text-slate-600">none recorded</p>}
                  {(s?.locations ?? []).map(([l, n]: [string, number]) => (
                    <div key={l} className="flex justify-between font-mono text-[11px] text-slate-300">
                      <span>{l}</span>
                      <span className="text-slate-500">×{n}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 max-h-56 overflow-y-auto rounded-lg border border-cyber-cyan/10 bg-ink-850">
                <table className="w-full text-left font-mono text-[11px]">
                  <thead className="sticky top-0 bg-ink-850 text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Time</th>
                      <th className="px-3 py-2">Ref</th>
                      <th className="px-3 py-2">Counterparty</th>
                      <th className="px-3 py-2 text-right">Amount</th>
                      <th className="px-3 py-2">Decision</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(p.recent_transactions ?? []).slice(0, 20).map((t: any) => (
                      <tr key={t.txn_ref} className="border-t border-ink-800/50">
                        <td className="px-3 py-1.5 text-slate-400">{fmtDateTime(t.txn_time)}</td>
                        <td className="px-3 py-1.5 text-cyber-cyan/70">{shortRef(t.txn_ref)}</td>
                        <td className="px-3 py-1.5 text-slate-300">
                          {shortRef(t.source_ref === p.account.account_ref ? t.dest_ref : t.source_ref)}
                        </td>
                        <td className="px-3 py-1.5 text-right text-slate-200">{fmtInr(t.amount)}</td>
                        <td className="px-3 py-1.5">
                          <DecisionBadge decision={t.risk_decision} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="space-y-4">
              <div className="panel p-5">
                <h3 className="mb-3 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                  <GitBranch className="h-3.5 w-3.5 text-cyber-cyan" /> Top Counterparties
                </h3>
                <div className="space-y-2">
                  {(s?.top_counterparties ?? []).slice(0, 8).map(([acc, n]: [string, number], i: number) => (
                    <button
                      key={acc}
                      onClick={() => run(acc)}
                      className="flex w-full items-center gap-2 rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2 text-left transition-colors hover:border-cyber-cyan/40"
                    >
                      <span className="font-mono text-[10px] text-slate-600">#{i + 1}</span>
                      <span className="flex-1 truncate font-mono text-[11px] text-slate-300">{acc}</span>
                      <span className="font-mono text-[10px] text-slate-500">×{n}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="panel p-5">
                <h3 className="mb-3 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                  Decisions
                </h3>
                <div className="space-y-1.5 font-mono text-[11px]">
                  {Object.entries(s?.decisions ?? {}).map(([d, n]) => (
                    <div key={d} className="flex items-center justify-between">
                      <span className="text-slate-400">{d}</span>
                      <span className="tabular-nums text-slate-200">{n as number}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="panel p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="flex items-center gap-2 font-display text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
                <Network className="h-4 w-4 text-cyber-cyan" /> Fund-Trail Network
              </h2>
              <div className="flex gap-2">
                {trailLoading && (
                  <span className="font-mono text-[10px] text-slate-500">
                    building graph<span className="cursor-blink" />
                  </span>
                )}
                <span className="chip border border-cyber-cyan/20 bg-cyber-cyan/5 text-cyber-cyan">
                  {trail?.stats ? `${trail.stats.nodes} nodes · ${trail.stats.edges} edges · ₹${(trail.stats.volume ?? 0).toLocaleString("en-IN")}` : "—"}
                </span>
              </div>
            </div>
            <div className="graph-grid h-[430px] overflow-hidden rounded-lg border border-cyber-cyan/10 bg-ink-950/60">
              {trail ? (
                <FundTrailGraph nodes={trail.nodes} edges={trail.edges} clusters={trail.clusters} />
              ) : (
                <div className="flex h-full items-center justify-center font-mono text-xs text-slate-500">
                  {trailLoading ? "tracing money flow…" : "no graph data"}
                </div>
              )}
            </div>
            {trail?.clusters?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {trail.clusters.map((c: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="flex items-center gap-2 rounded-md border border-cyber-red/25 bg-cyber-red/5 px-3 py-1.5 font-mono text-[11px] text-cyber-red"
                  >
                    <ShieldAlert className="h-3.5 w-3.5" />
                    {c.label}
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}