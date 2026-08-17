import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldAlert, ShieldOff, Upload, Search, Flag, Download } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api, uploadCsv } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

export function FlaggedAccounts() {
  const { token } = useAuth();
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [ref, setRef] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<any>("/flagged", token);
      setRows(data.flagged ?? []);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, [load]);

  const addFlag = async () => {
    if (!ref.trim()) return;
    setBusy(true);
    setMsg("");
    try {
      await api.post("/flagged", { account_ref: ref.trim(), reason: reason.trim(), severity: "HIGH" }, token);
      setRef("");
      setReason("");
      setMsg(`Flagged ${ref.trim()} — future transactions will be auto-blocked.`);
      await load();
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const removeFlag = async (accountRef: string) => {
    try {
      await api.post("/flagged/unflag", { account_ref: accountRef }, token);
      await load();
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  };

  const onFile = async (file: File) => {
    setBusy(true);
    setMsg("");
    try {
      const res: any = await uploadCsv(file, token ?? "");
      setMsg(`Imported ${res.imported ?? 0} suspect accounts from ${file.name}.`);
      await load();
    } catch (e: any) {
      setMsg(`Import failed: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const exportCsv = () => {
    const header = "account_ref,reason,severity,source,created_at";
    const body = rows.map((r) => `"${r.account_ref}","${(r.reason ?? "").replace(/"/g, '""')}","${r.severity}","${r.source}","${r.created_at}"`).join("\n");
    const blob = new Blob([`${header}\n${body}`], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "ffmitra-flagged-accounts.csv";
    a.click();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Flagged Accounts</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">
            watchlist & blacklist · enforcement is instant
          </p>
        </div>
        <div className="flex gap-2">
          <label className="btn-ghost cursor-pointer">
            <Upload className="h-4 w-4" /> Import Suspect List
            <input
              type="file"
              accept=".csv,.json"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
            />
          </label>
          <button className="btn-ghost" onClick={exportCsv} disabled={rows.length === 0}>
            <Download className="h-4 w-4" /> Export
          </button>
        </div>
      </div>

      <div className="panel grid grid-cols-1 gap-3 p-4 sm:grid-cols-[1fr_1fr_auto]">
        <input className="input" placeholder="Account / UPI ID to flag, e.g. mule.vendor@paytm" value={ref} onChange={(e) => setRef(e.target.value)} />
        <input className="input" placeholder="Reason (optional)" value={reason} onChange={(e) => setReason(e.target.value)} />
        <button className="btn-danger" onClick={addFlag} disabled={busy || !ref.trim()}>
          <Flag className="h-4 w-4" /> Flag Account
        </button>
      </div>

      <AnimatePresence>
        {msg && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="rounded-lg border border-cyber-cyan/25 bg-cyber-cyan/5 px-4 py-3 font-mono text-xs text-cyber-cyan"
          >
            {msg}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="panel overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-cyber-cyan/10 bg-ink-850/60 font-mono text-[10px] uppercase tracking-[0.15em] text-slate-500">
              <th className="px-4 py-3">Account</th>
              <th className="px-4 py-3">Severity</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Reason</th>
              <th className="px-4 py-3">Flagged</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center font-mono text-xs text-slate-500">
                  loading watchlist<span className="cursor-blink" />
                </td>
              </tr>
            )}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center font-mono text-xs text-slate-500">
                  watchlist empty — flag an account or import a suspect list
                </td>
              </tr>
            )}
            {!loading &&
              rows.map((r) => (
                <tr key={r.id} className="border-b border-ink-800/60 transition-colors hover:bg-cyber-cyan/5">
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2 font-mono text-xs text-slate-200">
                      <ShieldAlert className="h-3.5 w-3.5 text-cyber-red" /> {r.account_ref}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`chip border ${r.severity === "HIGH" ? "border-cyber-red/40 bg-cyber-red/10 text-cyber-red" : "border-cyber-amber/40 bg-cyber-amber/10 text-cyber-amber"}`}>
                      {r.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{r.source}</td>
                  <td className="max-w-[260px] truncate px-4 py-3 text-xs text-slate-400">{r.reason || "—"}</td>
                  <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{timeAgo(r.created_at)}</td>
                  <td className="px-4 py-3 text-right">
                    <button className="btn-ghost px-2.5 py-1 text-[11px]" onClick={() => removeFlag(r.account_ref)}>
                      <ShieldOff className="h-3.5 w-3.5" /> Unflag
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}