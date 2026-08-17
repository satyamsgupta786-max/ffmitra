import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileBarChart, Download, FileText } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { fmtDateTime } from "@/lib/utils";

export function Reports() {
  const { token } = useAuth();
  const [txns, setTxns] = useState<any[]>([]);
  const [flagged, setFlagged] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<any>("/transactions?limit=500", token),
      api.get<any>("/flagged", token),
      api.get<any>("/cases?limit=200", token),
    ])
      .then(([t, f, c]) => {
        setTxns(t.transactions ?? []);
        setFlagged(f.flagged ?? []);
        setCases(c.cases ?? []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [token]);

  const blocked = txns.filter((t) => t.risk_decision === "BLOCK");
  const review = txns.filter((t) => t.risk_decision === "REVIEW");
  const volume = txns.reduce((s, t) => s + Number(t.amount ?? 0), 0);
  const blockedVolume = blocked.reduce((s, t) => s + Number(t.amount ?? 0), 0);

  const makeReport = (rows: any[], filename: string, columns: string[], mapper: (r: any) => string[]) => {
    const header = columns.join(",");
    const body = rows.map((r) => mapper(r).map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([`${header}\n${body}`], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
  };

  const summary = () =>
    makeReport(
      [
        { label: "Generated", value: new Date().toISOString() },
        { label: "Transactions analyzed", value: txns.length },
        { label: "Blocked", value: blocked.length },
        { label: "Review queue", value: review.length },
        { label: "Total volume", value: `₹${volume.toLocaleString("en-IN")}` },
        { label: "Blocked volume", value: `₹${blockedVolume.toLocaleString("en-IN")}` },
        { label: "Flagged accounts", value: flagged.length },
        { label: "Open cases", value: cases.filter((c) => c.status === "OPEN").length },
      ],
      "ffmitra-summary.csv",
      ["metric", "value"],
      (r) => [r.label, String(r.value)]
    );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Reports</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">regulatory & investigation exports</p>
        </div>
        <button className="btn-primary" onClick={summary} disabled={loading}>
          <Download className="h-4 w-4" /> Download Summary
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {[
          { label: "Blocked Transactions", value: blocked.length, accent: "#FF3B5C", desc: "auto-enforced fraud attempts" },
          { label: "Under Review", value: review.length, accent: "#FFB020", desc: "queued for analyst decision" },
          { label: "Volume Monitored", value: `₹${Math.round(volume / 1000)}k`, accent: "#00E5FF", desc: "across analyzed window" },
        ].map((c, i) => (
          <motion.div key={c.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="panel p-5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-slate-400">{c.label}</span>
              <FileBarChart className="h-4 w-4" style={{ color: c.accent }} />
            </div>
            <div className="mt-2 font-display text-3xl font-bold tabular-nums" style={{ color: c.accent }}>{c.value}</div>
            <div className="mt-1 font-mono text-[10.5px] text-slate-500">{c.desc}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="panel p-5">
          <h3 className="mb-3 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            <FileText className="h-3.5 w-3.5 text-cyber-red" /> Fraud Ledger
          </h3>
          <div className="max-h-72 space-y-1.5 overflow-y-auto">
            {blocked.length === 0 && <p className="font-mono text-[11px] text-slate-600">no blocked transactions yet</p>}
            {blocked.slice(0, 30).map((t) => (
              <div key={t.txn_ref} className="rounded-md border border-cyber-red/20 bg-cyber-red/5 px-3 py-2 font-mono text-[10.5px]">
                <div className="flex justify-between text-slate-300">
                  <span>{t.txn_ref}</span>
                  <span className="text-cyber-red">₹{Number(t.amount).toLocaleString("en-IN")}</span>
                </div>
                <div className="text-slate-500">{t.source_ref} → {t.dest_ref} · {fmtDateTime(t.txn_time)}</div>
              </div>
            ))}
          </div>
          <button className="btn-ghost mt-3 w-full" onClick={() => makeReport(blocked, "ffmitra-blocked.csv", ["txn_ref", "time", "from", "to", "amount", "risk", "reasons"], (t) => [t.txn_ref, t.txn_time, t.source_ref, t.dest_ref, String(t.amount), String(Math.round(t.risk_score ?? 0)), (t.risk_reasons ?? []).join("; ")])}>
            <Download className="h-3.5 w-3.5" /> Export Fraud Ledger
          </button>
        </div>

        <div className="panel p-5">
          <h3 className="mb-3 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            <FileText className="h-3.5 w-3.5 text-cyber-amber" /> Review Queue
          </h3>
          <div className="max-h-72 space-y-1.5 overflow-y-auto">
            {review.length === 0 && <p className="font-mono text-[11px] text-slate-600">queue clear</p>}
            {review.slice(0, 30).map((t) => (
              <div key={t.txn_ref} className="rounded-md border border-cyber-amber/20 bg-cyber-amber/5 px-3 py-2 font-mono text-[10.5px]">
                <div className="flex justify-between text-slate-300">
                  <span>{t.txn_ref}</span>
                  <span className="text-cyber-amber">₹{Number(t.amount).toLocaleString("en-IN")}</span>
                </div>
                <div className="text-slate-500">{t.source_ref} → {t.dest_ref}</div>
              </div>
            ))}
          </div>
          <button className="btn-ghost mt-3 w-full" onClick={() => makeReport(review, "ffmitra-review-queue.csv", ["txn_ref", "time", "from", "to", "amount", "risk"], (t) => [t.txn_ref, t.txn_time, t.source_ref, t.dest_ref, String(t.amount), String(Math.round(t.risk_score ?? 0))])}>
            <Download className="h-3.5 w-3.5" /> Export Review Queue
          </button>
        </div>

        <div className="panel p-5">
          <h3 className="mb-3 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            <FileText className="h-3.5 w-3.5 text-cyber-green" /> Cases & Watchlist
          </h3>
          <div className="max-h-72 space-y-1.5 overflow-y-auto">
            {cases.map((c) => (
              <div key={c.id} className="rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2 font-mono text-[10.5px]">
                <div className="flex justify-between text-slate-300">
                  <span>{c.case_no}</span>
                  <span className="text-slate-500">{c.status}</span>
                </div>
                <div className="text-slate-500">{c.title}</div>
              </div>
            ))}
            {flagged.map((f) => (
              <div key={f.id} className="rounded-md border border-cyber-red/20 bg-cyber-red/5 px-3 py-2 font-mono text-[10.5px] text-slate-300">
                ⚑ {f.account_ref} · {f.severity}
              </div>
            ))}
          </div>
          <button className="btn-ghost mt-3 w-full" onClick={() => makeReport([...cases.map((c) => ({ type: "CASE", ref: c.case_no, label: c.title, meta: c.status })), ...flagged.map((f) => ({ type: "FLAGGED", ref: f.account_ref, label: f.reason || "suspect", meta: f.severity }))], "ffmitra-cases-watchlist.csv", ["type", "ref", "label", "meta"], (r) => [r.type, r.ref, r.label, r.meta])}>
            <Download className="h-3.5 w-3.5" /> Export Cases & Watchlist
          </button>
        </div>
      </div>
    </div>
  );
}