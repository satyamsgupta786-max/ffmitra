import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link2, ScanSearch, ShieldCheck, ShieldAlert, AlertTriangle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";

const EXAMPLES = [
  "http://hdfc-secure-login.xyz/verify",
  "https://www.paytm.com/recharge",
  "http://192.168.0.15/bank/login.php",
  "https://icici-update-refund.xyz/claim",
  "https://www.amazon.in/gp/help",
];

export function LinkAnalyzer() {
  const { token } = useAuth();
  const [url, setUrl] = useState("");
  const [sender, setSender] = useState("");
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  const analyze = async (u?: string) => {
    const target = (u ?? url).trim();
    if (!target) return;
    setBusy(true);
    try {
      const data = await api.post<any>("/links/analyze", { url: target, sender: sender.trim() || null }, token);
      setResult(data);
      setUrl(target);
    } catch {
      /* ignore */
    } finally {
      setBusy(false);
    }
  };

  const levelColor =
    result?.level === "HIGH" ? "#FF3B5C" : result?.level === "MEDIUM" ? "#FFB020" : "#00FF9D";
  const LevelIcon = result?.level === "HIGH" ? ShieldAlert : result?.level === "MEDIUM" ? AlertTriangle : ShieldCheck;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="font-display text-2xl font-bold text-slate-100">Link Analyzer</h1>
        <p className="mt-0.5 font-mono text-xs text-slate-500">
          AI-assisted phishing & scam-link inspection
        </p>
      </div>

      <div className="panel p-5">
        <label className="label">URL to inspect</label>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Link2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input className="input pl-9" placeholder="https://…" value={url} onChange={(e) => setUrl(e.target.value)} onKeyDown={(e) => e.key === "Enter" && analyze()} />
          </div>
          <button className="btn-primary" onClick={() => analyze()} disabled={busy || !url.trim()}>
            <ScanSearch className="h-4 w-4" /> {busy ? "Scanning…" : "Analyze"}
          </button>
        </div>
        <div className="mt-3">
          <label className="label">Sender (optional)</label>
          <input className="input" placeholder="e.g. +91 98765 43210 · hdfc-cares" value={sender} onChange={(e) => setSender(e.target.value)} />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="rounded-md border border-cyber-cyan/15 bg-ink-850 px-2.5 py-1 font-mono text-[10.5px] text-slate-400 transition-colors hover:border-cyber-cyan/40 hover:text-cyber-cyan" onClick={() => analyze(ex)}>
              {ex}
            </button>
          ))}
        </div>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="panel p-6">
            <div className="flex items-center gap-5">
              <motion.div
                key={result.risk_score}
                initial={{ scale: 0.7, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex h-24 w-24 shrink-0 flex-col items-center justify-center rounded-full border-2"
                style={{ borderColor: levelColor, boxShadow: `0 0 24px ${levelColor}44`, color: levelColor }}
              >
                <LevelIcon className="h-6 w-6" />
                <span className="mt-0.5 font-display text-xl font-bold tabular-nums">{result.risk_score}</span>
                <span className="font-mono text-[8.5px] uppercase tracking-[0.2em]">risk</span>
              </motion.div>
              <div className="min-w-0">
                <div className="mb-1 flex items-center gap-2">
                  <span className="chip" style={{ background: `${levelColor}1a`, color: levelColor, border: `1px solid ${levelColor}44` }}>
                    {result.level}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">
                    url {result.url_score} · sender {result.sender_score}
                  </span>
                </div>
                <p className="break-all font-mono text-xs text-cyber-cyan/80">{result.url}</p>
                <p className="mt-2 text-sm text-slate-300">{result.recommendation}</p>
              </div>
            </div>

            <div className="mt-5">
              <h3 className="mb-2 font-display text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Indicators detected
              </h3>
              <div className="space-y-1.5">
                {result.reasons.length === 0 && (
                  <p className="font-mono text-xs text-slate-500">no suspicious indicators found</p>
                )}
                {result.reasons.map((r: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-start gap-3 rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2"
                  >
                    <div className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: r.impact >= 0.5 ? "#FF3B5C" : r.impact >= 0.25 ? "#FFB020" : "#7C5CFF" }} />
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-slate-200">{r.label}</div>
                      <div className="font-mono text-[10.5px] text-slate-500">{r.detail}</div>
                    </div>
                    <span className="font-mono text-[10px] tabular-nums text-slate-500">+{(r.impact * 100).toFixed(0)}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}