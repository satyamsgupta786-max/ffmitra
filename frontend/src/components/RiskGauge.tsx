import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { riskColor } from "@/lib/utils";

export function RiskGauge({ score, size = 160 }: { score: number; size?: number }) {
  const [display, setDisplay] = useState(0);
  const color = riskColor(score);
  const r = (size - 26) / 2;
  const circ = 2 * Math.PI * r;
  const frac = Math.min(display / 100, 1);
  const sweep = circ * 0.75 * frac;
  const startAngle = 135;

  useEffect(() => {
    const t = setTimeout(() => setDisplay(score), 80);
    return () => clearTimeout(t);
  }, [score]);

  const angle = startAngle + 270 * frac;
  const rad = (angle * Math.PI) / 180;
  const tipX = size / 2 + r * Math.cos(rad);
  const tipY = size / 2 + r * Math.sin(rad);

  return (
    <div className="relative inline-flex flex-col items-center" style={{ width: size, height: size + 34 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="gaugeGrad" x1="0" y1="1" x2="1" y2="0">
            <stop offset="0%" stopColor="#00FF9D" />
            <stop offset="45%" stopColor="#FFB020" />
            <stop offset="100%" stopColor="#FF3B5C" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(148,163,184,0.12)"
          strokeWidth={12}
          strokeDasharray={`${circ * 0.75} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(${startAngle - 90} ${size / 2} ${size / 2})`}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="url(#gaugeGrad)"
          strokeWidth={12}
          strokeDasharray={`${sweep} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(${startAngle - 90} ${size / 2} ${size / 2})`}
          style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: "stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1)" }}
        />
        {display > 5 && (
          <motion.line
            x1={size / 2}
            y1={size / 2}
            x2={tipX}
            y2={tipY}
            stroke={color}
            strokeWidth={2.5}
            strokeLinecap="round"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            style={{ filter: `drop-shadow(0 0 4px ${color})` }}
          />
        )}
      </svg>
      <div className="absolute inset-x-0 top-[calc(50%-14px)] flex flex-col items-center">
        <motion.div
          key={Math.round(display)}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="font-display text-4xl font-bold tabular-nums"
          style={{ color, textShadow: `0 0 18px ${color}66` }}
        >
          {Math.round(display)}
        </motion.div>
        <div className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.25em] text-slate-400">
          Risk Score
        </div>
      </div>
    </div>
  );
}