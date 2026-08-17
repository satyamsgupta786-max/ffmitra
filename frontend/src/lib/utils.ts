export function fmtInr(value: number | null | undefined): string {
  const n = Number(value ?? 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(n);
}

export function fmtTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function riskColor(score: number): string {
  if (score >= 85) return "#FF3B5C";
  if (score >= 60) return "#FFB020";
  if (score >= 30) return "#7C5CFF";
  return "#00FF9D";
}

export function decisionMeta(decision: string) {
  switch (decision) {
    case "BLOCK":
      return { label: "BLOCK", color: "#FF3B5C", bg: "rgba(255,59,92,0.12)", border: "rgba(255,59,92,0.4)" };
    case "REVIEW":
      return { label: "REVIEW", color: "#FFB020", bg: "rgba(255,176,32,0.1)", border: "rgba(255,176,32,0.4)" };
    default:
      return { label: "APPROVE", color: "#00FF9D", bg: "rgba(0,255,157,0.08)", border: "rgba(0,255,157,0.35)" };
  }
}

export function truncate(text: string, len = 28): string {
  return text.length > len ? `${text.slice(0, len)}…` : text;
}

export function shortRef(ref: string): string {
  return ref.length > 22 ? `${ref.slice(0, 10)}…${ref.slice(-8)}` : ref;
}