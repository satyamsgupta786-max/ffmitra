import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, X, ArrowUpDown, RefreshCw } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { DecisionBadge } from "@/components/DecisionBadge";
import { RiskGauge } from "@/components/RiskGauge";
import { fmtDateTime, fmtInr, shortRef } from "@/lib/utils";

export function Transactions() {
  const { token } = useAuth();
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [decision, setDecision] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (q) params.set("q", q);
      if (decision) params.set("decision", decision);
      const data = await api.get<any>(`/transactions?${params}`, token);
      setRows(data.transactions ?? []);
      setTotal(data.count ?? 0);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [token, q, decision]);

  useEffect(() => {
    const t = setTimeout(load, q ? 350 : 0);
    return () => clearTimeout(t);
  }, [load, q]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Transactions</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">
            {total.toLocaleString()} records · real-time scored
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              className="input w-72 pl-9"
              placeholder="Search Txn ID / UTR / account…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <select className="input w-36" value={decision} onChange={(e) => setDecision(e.target.value)}>
            <option value="">All decisions</option>
            <option value="BLOCK">BLOCK</option>
            <option value="REVIEW">REVIEW</option>
            <option value="APPROVE">APPROVE</option>
          </select>
          <button className="btn-ghost" onClick={load} title="Refresh">
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-cyber-cyan/10 bg-ink-850/60 font-mono text-[10px] uppercase tracking-[0.15em] text-slate-500">
                <th className="px-4 py-3">Txn Ref</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">From</th>
                <th className="px-4 py-3">To</th>
                <th className="px-4 py-3 text-right">Amount</th>
                <th className="px-4 py-3">Channel</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Decision</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={9} className="px-4 py-10 text-center font-mono text-xs text-slate-500">
                    scanning ledger<span className="cursor-blink" />
                  </td>
                </tr>
              )}
              {!loading && rows.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-4 py-10 text-center font-mono text-xs text-slate-500">
                    no transactions found
                  </td>
                </tr>
              )}
              {!loading &&
                rows.map((t) => (
                  <tr
                    key={t.txn_ref}
                    className="cursor-pointer border-b border-ink-800/60 transition-colors hover:bg-cyber-cyan/5"
                    onClick={() => setSelected(t)}
                  >
                    <td className="px-4 py-2.5 font-mono text-xs text-cyber-cyan/80">{shortRef(t.txn_ref)}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-400">{fmtDateTime(t.txn_time)}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-300">{shortRef(t.source_ref)}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-300">{shortRef(t.dest_ref)}</td>
                    <td className="px-4 py-2.5 text-right font-semibold tabular-nums text-slate-100">{fmtInr(t.amount)}</td>
                    <td className="px-4 py-2.5 font-mono text-[11px] text-slate-500">{t.channel}</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-ink-800">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${Math.min(t.risk_score ?? 0, 100)}%`,
                              background:
                                (t.risk_score ?? 0) >= 85 ? "#FF3B5C" : (t.risk_score ?? 0) >= 60 ? "#FFB020" : (t.risk_score ?? 0) >= 30 ? "#7C5CFF" : "#00FF9D",
                            }}
                          />
                        </div>
                        <span className="font-mono text-xs tabular-nums text-slate-300">{Math.round(t.risk_score ?? 0)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <DecisionBadge decision={t.risk_decision} pulse />
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <ArrowUpDown className="h-3.5 w-3.5 text-slate-600" />
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex justify-end bg-ink-950/70 backdrop-blur-sm"
            onClick={() => setSelected(null)}
          >
            <motion.div
              initial={{ x: 420 }}
              animate={{ x: 0 }}
              exit={{ x: 420 }}
              transition={{ type: "spring", damping: 28, stiffness: 260 }}
              className="h-full w-[440px] overflow-y-auto border-l border-cyber-cyan/15 bg-ink-900 p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-5 flex items-center justify-between">
                <h2 className="font-display text-lg font-bold text-slate-100">Transaction Analysis</h2>
                <button className="rounded p-1.5 text-slate-500 hover:bg-ink-800" onClick={() => setSelected(null)}>
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="mb-4 font-mono text-xs text-cyber-cyan/80">{selected.txn_ref}</div>

              <div className="mb-5 flex justify-center">
                <RiskGauge score={Number(selected.risk_score ?? 0)} size={150} />
              </div>
              <div className="mb-5 flex justify-center">
                <DecisionBadge decision={selected.risk_decision} />
              </div>

              <div className="space-y-2.5 rounded-lg border border-cyber-cyan/10 bg-ink-850 p-4 font-mono text-xs">
                {[
                  ["Time", fmtDateTime(selected.txn_time)],
                  ["From", selected.source_ref],
                  ["To", selected.dest_ref],
                  ["Amount", fmtInr(selected.amount)],
                  ["Channel", `${selected.channel} · ${selected.txn_type}`],
                  ["Device", selected.device_id ?? "—"],
                  ["IP", selected.ip_address ?? "—"],
                  ["Location", selected.location ?? "—"],
                  ["Merchant", selected.merchant ?? "—"],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4">
                    <span className="shrink-0 text-slate-500">{k}</span>
                    <span className="break-all text-right text-slate-200">{v}</span>
                  </div>
                ))}
              </div>

              <h3 className="mb-2 mt-5 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Reasons
              </h3>
              <div className="space-y-1.5">
                {(selected.risk_reasons ?? []).length === 0 && (
                  <p className="font-mono text-xs text-slate-500">No risk flags — transaction cleared.</p>
                )}
                {(selected.risk_reasons ?? []).map((r: string, i: number) => (
                  <div key={i} className="flex gap-2 rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2 font-mono text-[11px] text-slate-300">
                    <span className="text-cyber-cyan">▸</span> {r}
                  </div>
                ))}
              </div>

              {(selected.meta?.shap?.length ?? 0) > 0 && (
                <>
                  <h3 className="mb-2 mt-5 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                    Model Attribution (SHAP)
                  </h3>
                  <div className="space-y-1.5">
                    {selected.meta.shap.map((s: any, i: number) => (
                      <div key={i} className="rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2">
                        <div className="flex justify-between font-mono text-[11px]">
                          <span className="text-slate-300">{s.label}</span>
                          <span className={s.impact > 0 ? "text-cyber-red" : "text-cyber-green"}>
                            {s.impact > 0 ? "+" : ""}
                            {s.impact.toFixed(3)}
                          </span>
                        </div>
                        <div className="mt-1 h-1 overflow-hidden rounded bg-ink-800">
                          <div
                            className={`h-full ${s.impact > 0 ? "bg-cyber-red" : "bg-cyber-green"}`}
                            style={{ width: `${Math.min(Math.abs(s.impact) * 200, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}