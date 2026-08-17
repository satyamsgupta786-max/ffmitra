import { decisionMeta, fmtInr, fmtTime, riskColor, shortRef } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldAlert, ShieldCheck, Radar } from "lucide-react";

type Row = {
  kind: "txn" | "alert";
  data: any;
};

export function LiveFeed({ rows }: { rows: Row[] }) {
  if (rows.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 py-10 text-slate-500">
        <Radar className="h-8 w-8 animate-pulse text-cyber-cyan/50" />
        <p className="font-mono text-xs tracking-wider">
          awaiting live transaction stream<span className="cursor-blink" />
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex-1 space-y-1 overflow-y-auto pr-1 font-mono text-[12.5px]">
        <AnimatePresence initial={false}>
          {rows.map((row) => {
            const d = row.data;
            if (row.kind === "alert") {
              const sev = d.severity === "HIGH" ? "#FF3B5C" : d.severity === "MEDIUM" ? "#FFB020" : "#7C5CFF";
              return (
                <motion.div
                  key={`a-${d.id}-${d.ts ?? Date.now()}`}
                  initial={{ opacity: 0, x: 24 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-start gap-2 rounded border border-cyber-red/25 bg-cyber-red/5 px-2.5 py-1.5"
                  style={{ boxShadow: `inset 2px 0 0 ${sev}` }}
                >
                  <ShieldAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" style={{ color: sev }} />
                  <div className="min-w-0">
                    <span className="text-slate-300">{d.title}</span>
                    <span className="ml-1.5 text-slate-500">{fmtTime(d.created_at)}</span>
                  </div>
                </motion.div>
              );
            }
            const meta = decisionMeta(d.risk_decision ?? "APPROVE");
            const color = riskColor(Number(d.risk_score) ?? 0);
            return (
              <motion.div
                key={`t-${d.id}-${d.txn_ref}`}
                initial={{ opacity: 0, x: 24 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2 px-2.5 py-1.5 transition-colors hover:bg-ink-800/60"
              >
                <span className="text-slate-600">{fmtTime(d.txn_time)}</span>
                <span className="w-10 shrink-0 text-[10px] text-slate-500">{d.channel ?? "UPI"}</span>
                <span className="text-cyber-cyan/80">{shortRef(d.source_ref ?? "")}</span>
                <span className="text-slate-600">→</span>
                <span className="max-w-[130px] truncate text-slate-300">{shortRef(d.dest_ref ?? "")}</span>
                <span className="ml-auto font-semibold tabular-nums" style={{ color }}>
                  {fmtInr(d.amount)}
                </span>
                <span
                  className="rounded px-1.5 py-0.5 text-[10px] font-bold tracking-wider"
                  style={{ color: meta.color, background: meta.bg }}
                >
                  {meta.label}
                </span>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
      <div className="flex items-center justify-between border-t border-cyber-cyan/10 px-2.5 py-1.5 font-mono text-[10px] text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyber-green" />
          LIVE {rows.length > 0 && <ShieldCheck className="h-3 w-3 text-cyber-green" />}
        </span>
        <span>{rows.length} events buffered</span>
      </div>
    </div>
  );
}