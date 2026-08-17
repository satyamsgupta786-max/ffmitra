import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent: string;
  sub?: string;
  delay?: number;
};

export function KpiCard({ label, value, icon: Icon, accent, sub, delay = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="panel group relative overflow-hidden p-4"
    >
      <div
        className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full opacity-20 blur-2xl transition-opacity group-hover:opacity-40"
        style={{ background: accent }}
      />
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-slate-400">{label}</span>
        <Icon className="h-4 w-4" style={{ color: accent }} />
      </div>
      <motion.div
        key={String(value)}
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mt-2 font-display text-2xl font-bold tabular-nums text-slate-100"
      >
        {value}
      </motion.div>
      {sub && <div className="mt-0.5 font-mono text-[10px] text-slate-500">{sub}</div>}
    </motion.div>
  );
}