import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowLeftRight,
  ShieldAlert,
  ShieldCheck,
  Clock3,
  IndianRupee,
  Activity,
  Bell,
  AlertTriangle,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { useRealtimeStream } from "@/hooks/useRealtime";
import { KpiCard } from "@/components/KpiCard";
import { RiskGauge } from "@/components/RiskGauge";
import { LiveFeed } from "@/components/LiveFeed";
import { fmtInr, timeAgo } from "@/lib/utils";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";

const PIE_COLORS = ["#00FF9D", "#FFB020", "#FF3B5C"];

export function Dashboard() {
  const { token } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { items, alertPulse } = useRealtimeStream(50);

  const refresh = () => {
    api
      .get<any>("/dashboard/stats", token)
      .then((d) => {
        setStats(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 10000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const k = stats?.kpis ?? {};
  const pieData = [
    { name: "APPROVE", value: k.approved ?? 0 },
    { name: "REVIEW", value: k.review ?? 0 },
    { name: "BLOCK", value: k.blocked ?? 0 },
  ].filter((d) => d.value > 0);

  const hourly = (stats?.hourly ?? []).map((h: any) => ({
    ...h,
    label: h.bucket.slice(11, 16),
  }));

  const riskDist = stats?.risk_distribution ?? {};

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Command Center</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">
            live risk intelligence · all channels monitored
          </p>
        </div>
        {alertPulse > 0 && (
          <motion.div
            key={alertPulse}
            initial={{ scale: 0.6, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-2 rounded-lg border border-cyber-red/40 bg-cyber-red/10 px-3 py-2 font-mono text-xs text-cyber-red"
          >
            <Bell className="h-4 w-4" />
            {alertPulse} new alert{alertPulse > 1 ? "s" : ""} received
          </motion.div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 xl:grid-cols-5">
        <KpiCard label="Transactions" value={(k.transactions ?? 0).toLocaleString()} icon={ArrowLeftRight} accent="#00E5FF" sub="last 500 tracked" delay={0} />
        <KpiCard label="Blocked" value={k.blocked ?? 0} icon={ShieldAlert} accent="#FF3B5C" sub="auto-enforced" delay={0.05} />
        <KpiCard label="Review Queue" value={k.review ?? 0} icon={Clock3} accent="#FFB020" sub="needs analyst" delay={0.1} />
        <KpiCard label="Volume" value={fmtInr(k.total_volume ?? 0)} icon={IndianRupee} accent="#7C5CFF" sub="monitored window" delay={0.15} />
        <KpiCard label="Flagged Accounts" value={k.flagged_accounts ?? 0} icon={AlertTriangle} accent="#00FF9D" sub="watchlist active" delay={0.2} />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <div className="panel scanline relative flex items-center justify-center p-6">
          <div className="radar absolute inset-8 rounded-full border border-cyber-cyan/15" />
          <RiskGauge score={loading ? 0 : Math.min((k.blocked ?? 0) * 18 + 12, 99)} />
        </div>

        <div className="panel p-5 xl:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
              Transaction Throughput
            </h2>
            <span className="flex items-center gap-1.5 font-mono text-[10px] text-slate-500">
              <Activity className="h-3 w-3 text-cyber-cyan" /> last 24 buckets
            </span>
          </div>
          <ResponsiveContainer width="100%" height={190}>
            <AreaChart data={hourly}>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00E5FF" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#00E5FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="label" stroke="#334155" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#334155" fontSize={10} tickLine={false} axisLine={false} width={30} />
              <Tooltip
                contentStyle={{ background: "#0D1326", border: "1px solid rgba(0,229,255,0.25)", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#94A3B8" }}
              />
              <Area type="monotone" dataKey="count" stroke="#00E5FF" strokeWidth={2} fill="url(#areaGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <div className="panel p-5">
          <h2 className="mb-4 font-display text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
            Decision Mix
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} dataKey="value" innerRadius={52} outerRadius={78} paddingAngle={4} stroke="none">
                {pieData.map((entry, i) => (
                  <Cell key={entry.name} fill={PIE_COLORS[i % 3]} style={{ filter: "drop-shadow(0 0 6px rgba(0,229,255,0.25))" }} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: "#0D1326", border: "1px solid rgba(0,229,255,0.25)", borderRadius: 8, fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex justify-center gap-4">
            {pieData.map((d, i) => (
              <span key={d.name} className="flex items-center gap-1.5 font-mono text-[10px] text-slate-400">
                <span className="h-2 w-2 rounded-full" style={{ background: PIE_COLORS[i % 3] }} />
                {d.name} · {d.value}
              </span>
            ))}
          </div>
        </div>

        <div className="panel p-5">
          <h2 className="mb-4 font-display text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
            Risk Distribution
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={Object.entries(riskDist).map(([k, v]) => ({ name: k, value: v }))}>
              <XAxis dataKey="name" stroke="#334155" fontSize={9} tickLine={false} axisLine={false} />
              <YAxis stroke="#334155" fontSize={10} tickLine={false} axisLine={false} width={30} />
              <Tooltip
                cursor={{ fill: "rgba(0,229,255,0.05)" }}
                contentStyle={{ background: "#0D1326", border: "1px solid rgba(0,229,255,0.25)", borderRadius: 8, fontSize: 12 }}
              />
              <Bar dataKey="value" fill="#7C5CFF" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel p-5 xl:col-span-1">
          <h2 className="mb-4 flex items-center justify-between font-display text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">
            Live Feed
            <span className="flex items-center gap-1.5 font-mono text-[10px] font-normal text-cyber-green">
              <ShieldCheck className="h-3.5 w-3.5" /> realtime
            </span>
          </h2>
          <div className="h-[220px]">
            <LiveFeed rows={items} />
          </div>
        </div>
      </div>

      {stats?.alerts && stats.alerts > 0 && (
        <div className="panel flex items-center justify-between px-5 py-3">
          <span className="flex items-center gap-2 font-mono text-xs text-slate-400">
            <Bell className="h-4 w-4 text-cyber-amber" />
            {k.open_alerts ?? 0} unacknowledged alerts · {stats.alert_types ? Object.entries(stats.alert_types).map(([t, n]) => `${t}: ${n}`).join(" · ") : ""}
          </span>
          <span className="font-mono text-[10px] text-slate-600">updated {timeAgo(new Date().toISOString())}</span>
        </div>
      )}
    </div>
  );
}