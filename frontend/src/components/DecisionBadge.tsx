import { motion } from "framer-motion";
import { ShieldAlert, ShieldCheck, Clock3 } from "lucide-react";
import { decisionMeta } from "@/lib/utils";

export function DecisionBadge({ decision, pulse = false }: { decision: string; pulse?: boolean }) {
  const meta = decisionMeta(decision);
  const Icon = decision === "APPROVE" ? ShieldCheck : decision === "REVIEW" ? Clock3 : ShieldAlert;
  return (
    <motion.span
      className="inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11px] font-bold tracking-wider"
      style={{ color: meta.color, background: meta.bg, borderColor: meta.border }}
      animate={pulse && decision !== "APPROVE" ? { scale: [1, 1.06, 1] } : undefined}
      transition={{ duration: 1.2, repeat: Infinity }}
    >
      <Icon className="h-3.5 w-3.5" />
      {meta.label}
    </motion.span>
  );
}