import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Database, RefreshCw, Gauge, BrainCircuit } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";

export function Admin() {
  const { token } = useAuth();
  const [health, setHealth] = useState<any>(null);
  const [settings, setSettings] = useState<any>(null);
  const [system, setSystem] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = async () => {
    try {
      const [h, s, sys] = await Promise.all([
        api.get<any>("/admin/models/health", token),
        api.get<any>("/admin/settings", token),
        api.get<any>("/admin/system", token),
      ]);
      setHealth(h);
      setSettings(s);
      setSystem(sys);
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    load();
  }, [token]);

  const saveSettings = async () => {
    setBusy(true);
    setMsg("");
    try {
      const res = await api.patch<any>("/admin/settings", settings, token);
      setSettings(res);
      setMsg("Thresholds updated — engine will apply them immediately.");
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const retrain = async () => {
    setBusy(true);
    setMsg("");
    try {
      await api.post<any>("/admin/retrain", {}, token);
      setMsg("Retraining started in background. Models reload on next restart.");
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const metrics = health?.metrics ?? {};
  const artifacts = health?.artifacts ?? {};

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">System Admin</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">model health · thresholds · engine control</p>
        </div>
        <button className="btn-ghost" onClick={load}>
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {msg && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="rounded-lg border border-cyber-cyan/25 bg-cyber-cyan/5 px-4 py-3 font-mono text-xs text-cyber-cyan">
          {msg}
        </motion.div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="panel p-5">
          <h3 className="mb-4 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            <BrainCircuit className="h-4 w-4 text-cyber-cyan" /> Model Health
          </h3>
          <div className="space-y-2">
            {Object.entries(artifacts).map(([name, info]: [string, any]) => (
              <div key={name} className="flex items-center justify-between rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2">
                <span className="flex items-center gap-2 font-mono text-[11px] text-slate-300">
                  <Cpu className={`h-3.5 w-3.5 ${info.exists ? "text-cyber-green" : "text-cyber-red"}`} />
                  {name}
                </span>
                <span className="font-mono text-[10px] text-slate-500">
                  {info.exists ? `${(info.size_bytes / 1024).toFixed(0)} KB` : "MISSING"}
                </span>
              </div>
            ))}
          </div>
          {metrics && (
            <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {[
                ["Precision", metrics.precision],
                ["Recall", metrics.recall],
                ["F1", metrics.f1],
                ["PR-AUC", metrics.pr_auc],
              ].map(([label, value]) => (
                <div key={label as string} className="rounded-md border border-cyber-cyan/10 bg-ink-850 p-2.5 text-center">
                  <div className="font-mono text-[9px] uppercase tracking-wider text-slate-500">{label}</div>
                  <div className="mt-0.5 font-display text-base font-bold tabular-nums text-cyber-green">
                    {value != null ? (Number(value) * 100).toFixed(1) + "%" : "—"}
                  </div>
                </div>
              ))}
            </div>
          )}
          <button className="btn-ghost mt-4 w-full" onClick={retrain} disabled={busy}>
            <RefreshCw className={`h-4 w-4 ${busy ? "animate-spin" : ""}`} /> Retrain Models
          </button>
        </div>

        <div className="panel p-5">
          <h3 className="mb-4 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            <Gauge className="h-4 w-4 text-cyber-cyan" /> Scoring Thresholds
          </h3>
          {settings && (
            <div className="space-y-4">
              {[
                ["model_review", "Review threshold (0–1)"],
                ["model_block", "Block threshold (0–1)"],
                ["ml_weight", "ML model weight"],
                ["anomaly_weight", "Anomaly detector weight"],
                ["rule_weight", "Rule engine weight"],
              ].map(([key, label]) => (
                <div key={key}>
                  <div className="mb-1 flex justify-between font-mono text-[11px]">
                    <span className="text-slate-400">{label}</span>
                    <span className="text-cyber-cyan">{Number(settings[key]).toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={Number(settings[key])}
                    onChange={(e) => setSettings({ ...settings, [key]: Number(e.target.value) })}
                    className="w-full accent-cyan-400"
                  />
                </div>
              ))}
              <button className="btn-primary w-full" onClick={saveSettings} disabled={busy}>
                Apply Thresholds
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="panel p-5">
        <h3 className="mb-3 flex items-center gap-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
          <Database className="h-4 w-4 text-cyber-cyan" /> System Status
        </h3>
        <div className="grid grid-cols-1 gap-3 font-mono text-[11px] sm:grid-cols-3">
          <div className="rounded-md border border-cyber-cyan/10 bg-ink-850 p-3">
            <div className="text-slate-500">SUPABASE</div>
            <div className={`mt-1 text-sm font-semibold ${system?.db?.ok ? "text-cyber-green" : "text-cyber-red"}`}>
              {system?.db?.ok ? "CONNECTED" : "OFFLINE"}
            </div>
            <div className="text-slate-500">{system?.db?.transactions ?? 0} txns stored</div>
          </div>
          <div className="rounded-md border border-cyber-cyan/10 bg-ink-850 p-3">
            <div className="text-slate-500">SIMULATOR</div>
            <div className={`mt-1 text-sm font-semibold ${system?.simulator?.running ? "text-cyber-green" : "text-slate-400"}`}>
              {system?.simulator?.running ? "STREAMING" : "IDLE"}
            </div>
            <div className="text-slate-500">
              {system?.simulator?.counts ? `${system.simulator.counts.sent} sent · ${system.simulator.counts.blocked} blocked` : "—"}
            </div>
          </div>
          <div className="rounded-md border border-cyber-cyan/10 bg-ink-850 p-3">
            <div className="text-slate-500">ENGINE</div>
            <div className="mt-1 text-sm font-semibold text-cyber-green">OPERATIONAL</div>
            <div className="text-slate-500">{system?.status ?? "…"}</div>
          </div>
        </div>
      </div>
    </div>
  );
}