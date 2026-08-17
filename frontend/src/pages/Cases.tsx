import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FolderOpen, Plus, StickyNote, ChevronDown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  OPEN: "#00E5FF",
  INVESTIGATING: "#FFB020",
  RESOLVED: "#00FF9D",
  CLOSED: "#64748B",
};

const CATEGORIES = [
  "Payment / Transaction Fraud",
  "Phishing & Social Engineering",
  "Investment & Misleading Payments",
];

export function Cases() {
  const { token } = useAuth();
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [notes, setNotes] = useState<Record<number, any[]>>({});
  const [noteText, setNoteText] = useState("");
  const [form, setForm] = useState({ title: "", category: CATEGORIES[0], summary: "", victim_name: "", victim_contact: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<any>("/cases", token);
      setCases(data.cases ?? []);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const createCase = async () => {
    if (!form.title.trim()) return;
    try {
      await api.post("/cases", form, token);
      setForm({ title: "", category: CATEGORIES[0], summary: "", victim_name: "", victim_contact: "" });
      setShowCreate(false);
      await load();
    } catch {
      /* ignore */
    }
  };

  const toggleCase = async (id: number) => {
    if (expanded === id) {
      setExpanded(null);
      return;
    }
    setExpanded(id);
    try {
      const data = await api.get<any>(`/cases/${id}`, token);
      setNotes((prev) => ({ ...prev, [id]: data.notes ?? [] }));
    } catch {
      /* ignore */
    }
  };

  const addNote = async (caseId: number) => {
    if (!noteText.trim()) return;
    try {
      await api.post(`/cases/${caseId}/notes`, { note: noteText.trim() }, token);
      setNoteText("");
      const data = await api.get<any>(`/cases/${caseId}`, token);
      setNotes((prev) => ({ ...prev, [caseId]: data.notes ?? [] }));
    } catch {
      /* ignore */
    }
  };

  const setStatus = async (caseId: number, status: string) => {
    try {
      await api.patch(`/cases/${caseId}`, { status }, token);
      await load();
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Cases</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">victim reports · analyst workflows</p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate((v) => !v)}>
          <Plus className="h-4 w-4" /> New Case
        </button>
      </div>

      {showCreate && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="panel grid grid-cols-1 gap-3 p-4 md:grid-cols-2">
          <div>
            <label className="label">Case title</label>
            <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. UPI refund scam — victim lost ₹45,000" />
          </div>
          <div>
            <label className="label">Category</label>
            <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Victim name</label>
            <input className="input" value={form.victim_name} onChange={(e) => setForm({ ...form, victim_name: e.target.value })} />
          </div>
          <div>
            <label className="label">Victim contact</label>
            <input className="input" value={form.victim_contact} onChange={(e) => setForm({ ...form, victim_contact: e.target.value })} />
          </div>
          <div className="md:col-span-2">
            <label className="label">Summary</label>
            <textarea className="input" rows={3} value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} />
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button className="btn-primary" onClick={createCase} disabled={!form.title.trim()}>
              Create Case
            </button>
          </div>
        </motion.div>
      )}

      <div className="space-y-3">
        {loading && <div className="panel p-8 text-center font-mono text-xs text-slate-500">loading cases…</div>}
        {!loading && cases.length === 0 && (
          <div className="panel flex flex-col items-center gap-2 p-10 text-slate-500">
            <FolderOpen className="h-8 w-8 text-cyber-cyan/40" />
            <p className="font-mono text-xs">no cases yet — create one or let the victim assistant file reports</p>
          </div>
        )}
        {!loading &&
          cases.map((c) => (
            <motion.div key={c.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="panel overflow-hidden">
              <button className="flex w-full items-center gap-4 px-5 py-4 text-left" onClick={() => toggleCase(c.id)}>
                <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: STATUS_COLORS[c.status] ?? "#64748B", boxShadow: `0 0 8px ${STATUS_COLORS[c.status] ?? "#64748B"}` }} />
                <span className="w-28 shrink-0 font-mono text-xs text-cyber-cyan/70">{c.case_no}</span>
                <span className="flex-1 truncate font-medium text-slate-200">{c.title}</span>
                <span className="hidden max-w-[220px] truncate font-mono text-[11px] text-slate-500 md:block">{c.category}</span>
                <span className="chip border border-cyber-cyan/15 bg-ink-850 text-slate-300">{c.status}</span>
                <span className="hidden font-mono text-[10px] text-slate-600 sm:block">{timeAgo(c.created_at)}</span>
                <ChevronDown className={`h-4 w-4 text-slate-500 transition-transform ${expanded === c.id ? "rotate-180" : ""}`} />
              </button>

              {expanded === c.id && (
                <div className="border-t border-cyber-cyan/10 bg-ink-850/50 px-5 py-4">
                  <div className="mb-3 grid grid-cols-1 gap-2 font-mono text-[11px] text-slate-400 sm:grid-cols-3">
                    <span>Victim: <span className="text-slate-200">{c.victim_name || "—"}</span></span>
                    <span>Contact: <span className="text-slate-200">{c.victim_contact || "—"}</span></span>
                    <span>Source: <span className="text-slate-200">{c.source}</span></span>
                  </div>
                  {c.summary && <p className="mb-3 text-sm text-slate-300">{c.summary}</p>}

                  <div className="mb-3 flex flex-wrap gap-2">
                    {["OPEN", "INVESTIGATING", "RESOLVED", "CLOSED"].map((s) => (
                      <button
                        key={s}
                        onClick={() => setStatus(c.id, s)}
                        className={`rounded-md border px-3 py-1 font-mono text-[11px] transition-all ${
                          c.status === s
                            ? "border-cyber-cyan/40 bg-cyber-cyan/10 text-cyber-cyan"
                            : "border-ink-700 text-slate-500 hover:border-cyber-cyan/30 hover:text-slate-300"
                        }`}
                      >
                        {s}
                      </button>
                    ))}
                  </div>

                  <div className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
                    <StickyNote className="h-3 w-3" /> Analyst notes
                  </div>
                  <div className="mb-2 max-h-40 space-y-1.5 overflow-y-auto">
                    {(notes[c.id] ?? []).length === 0 && (
                      <p className="font-mono text-[11px] text-slate-600">no notes yet</p>
                    )}
                    {(notes[c.id] ?? []).map((n) => (
                      <div key={n.id} className="rounded-md border border-cyber-cyan/10 bg-ink-900 px-3 py-2">
                        <div className="text-sm text-slate-300">{n.note}</div>
                        <div className="mt-1 font-mono text-[10px] text-slate-600">
                          {n.author} · {timeAgo(n.created_at)}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input className="input" placeholder="Add an analyst note…" value={noteText} onChange={(e) => setNoteText(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addNote(c.id)} />
                    <button className="btn-ghost shrink-0" onClick={() => addNote(c.id)}>Add</button>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
      </div>
    </div>
  );
}