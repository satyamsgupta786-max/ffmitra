import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, MessageCircleHeart, PhoneCall, ShieldCheck, Siren, ArrowRight, Mic, Square } from "lucide-react";
import { api } from "@/lib/api";

const QUICK_ACTIONS = [
  "I lost money in a UPI scam, what do I do?",
  "Someone called pretending to be police (digital arrest)",
  "I invested in a trading app, they want more money",
  "My OTP was shared, money got deducted",
  "What is a mule account?",
  "How do I report to cybercrime?",
];

type Msg = { role: "user" | "assistant"; content: string; category?: string; urgency?: string };

export function VictimChat() {
  const [sessionRef, setSessionRef] = useState<string>("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [lastMeta, setLastMeta] = useState<any>(null);
  const [recording, setRecording] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    api.post<any>("/chat/session", {}).then((d) => setSessionRef(d.session_ref)).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  const sendVoice = async (blob: Blob) => {
    if (!sessionRef) {
      try {
        const d = await api.post<any>("/chat/session", {});
        setSessionRef(d.session_ref);
      } catch {
        return;
      }
    }
    setMessages((m) => [...m, { role: "user", content: "🎙️ (voice message)" }]);
    setBusy(true);
    setThinking(true);
    try {
      const form = new FormData();
      form.append("session_ref", sessionRef);
      form.append("audio", blob, "voice.webm");
      const res = await fetch(`/api/chat/voice`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (data.transcript) {
        setMessages((m) => [...m.slice(0, -1), { role: "user", content: `🎙️ "${data.transcript}"` }]);
      }
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
      setLastMeta({ category: data.category, urgency: data.urgency, used_llm: data.used_llm, suggest_report: data.suggest_report });
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "I couldn't hear you clearly. Please type your message, or call 1930 if money was lost." },
      ]);
    } finally {
      setBusy(false);
      setThinking(false);
    }
  };

  const toggleMic = async () => {
    if (recording) {
      mediaRef.current?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      chunksRef.current = [];
      rec.ondataavailable = (e) => chunksRef.current.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: rec.mimeType || "audio/webm" });
        if (blob.size > 0) sendVoice(blob);
      };
      mediaRef.current = rec;
      rec.start();
      setRecording(true);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Microphone unavailable in this browser. Please type your message instead." }]);
    }
  };

  const send = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || busy) return;
    if (!sessionRef) {
      try {
        const d = await api.post<any>("/chat/session", {});
        setSessionRef(d.session_ref);
      } catch {
        return;
      }
    }
    setMessages((m) => [...m, { role: "user", content }]);
    setInput("");
    setBusy(true);
    setThinking(true);
    try {
      const res = await api.post<any>("/chat/message", { session_ref: sessionRef, message: content });
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      setLastMeta({ category: res.category, urgency: res.urgency, used_llm: res.used_llm, suggest_report: res.suggest_report });
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "I'm unable to reach the assistant right now. Please call 1930 (cybercrime helpline) immediately if money was lost." },
      ]);
    } finally {
      setBusy(false);
      setThinking(false);
    }
  };

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-slate-100">Victim Assistant</h1>
          <p className="mt-0.5 font-mono text-xs text-slate-500">
            AI guidance for victims of cyber fraud · powered by Gemini + FFMitra knowledge base
          </p>
        </div>
        <span className="chip border border-cyber-green/30 bg-cyber-green/5 text-cyber-green">
          <ShieldCheck className="h-3 w-3" /> confidential · anonymous
        </span>
      </div>

      <div className="panel flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="border-b border-cyber-cyan/10 bg-ink-850/60 px-5 py-3">
          <div className="flex flex-wrap items-center gap-x-5 gap-y-1 font-mono text-[10px] uppercase tracking-[0.18em] text-slate-500">
            <span className="flex items-center gap-1.5 text-cyber-green">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyber-green" /> mitra online
            </span>
            {lastMeta?.category && <span>category: <span className="text-cyber-cyan">{lastMeta.category}</span></span>}
            {lastMeta?.urgency && (
              <span className={lastMeta.urgency === "CRITICAL" ? "text-cyber-red" : ""}>
                urgency: {lastMeta.urgency} {lastMeta.used_llm ? "· llm" : "· knowledge-base"}
              </span>
            )}
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <div className="relative flex h-20 w-20 items-center justify-center">
                <span className="absolute inset-0 animate-pulse-ring rounded-full border border-cyber-cyan/50" />
                <MessageCircleHeart className="relative h-9 w-9 text-cyber-cyan" />
              </div>
              <div className="max-w-md">
                <p className="font-display text-base font-semibold text-slate-200">
                  Namaste. I'm <span className="text-cyber-cyan">Mitra</span> — here to help you if you've been cheated or scammed online.
                </p>
                <p className="mt-2 text-sm text-slate-400">
                  Tell me what happened and I'll guide you step-by-step: what to do right now, how to report, what evidence to save.
                </p>
              </div>
              <div className="grid w-full max-w-xl grid-cols-1 gap-2 sm:grid-cols-2">
                {QUICK_ACTIONS.map((q) => (
                  <button key={q} className="rounded-lg border border-cyber-cyan/15 bg-ink-850 px-3 py-2.5 text-left text-xs text-slate-300 transition-all hover:border-cyber-cyan/40 hover:text-cyber-cyan" onClick={() => send(q)}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence initial={false}>
            {messages.map((m, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[78%] whitespace-pre-wrap rounded-xl px-4 py-3 text-sm leading-relaxed ${
                    m.role === "user"
                      ? "border border-cyber-cyan/40 bg-cyber-cyan/10 text-slate-100"
                      : "border border-ink-700 bg-ink-850 text-slate-200"
                  }`}
                >
                  {m.content}
                </div>
              </motion.div>
            ))}
            {thinking && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-xl border border-ink-700 bg-ink-850 px-4 py-3">
                  {[0, 1, 2].map((d) => (
                    <motion.span
                      key={d}
                      className="h-1.5 w-1.5 rounded-full bg-cyber-cyan"
                      animate={{ opacity: [0.2, 1, 0.2] }}
                      transition={{ duration: 1, repeat: Infinity, delay: d * 0.2 }}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {lastMeta?.suggest_report && (
          <div className="mx-5 mb-2 flex items-center justify-between rounded-lg border border-cyber-red/30 bg-cyber-red/10 px-4 py-2.5">
            <span className="flex items-center gap-2 font-mono text-xs text-cyber-red">
              <Siren className="h-4 w-4 animate-pulse" /> Time-critical: your case should be reported now.
            </span>
            <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs font-semibold text-cyber-red underline">
              Report on NCRP <ArrowRight className="h-3 w-3" />
            </a>
          </div>
        )}

        <div className="border-t border-cyber-cyan/10 p-4">
          <div className="flex gap-2">
            <button
              className={`shrink-0 rounded-lg border px-3 py-2 transition-all ${
                recording
                  ? "border-cyber-red bg-cyber-red/15 text-cyber-red"
                  : "border-cyber-cyan/25 bg-ink-850 text-cyber-cyan hover:border-cyber-cyan/50"
              }`}
              onClick={toggleMic}
              disabled={busy}
              title={recording ? "Stop and send voice note" : "Record voice note"}
            >
              {recording ? <Square className="h-4 w-4 animate-pulse" /> : <Mic className="h-4 w-4" />}
            </button>
            <input
              className="input"
              placeholder="Describe what happened… (e.g. UPI scam, fake call, trading app)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button className="btn-primary shrink-0" onClick={() => send()} disabled={busy || !input.trim()}>
              <Send className="h-4 w-4" /> Send
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between font-mono text-[10px] text-slate-600">
            <span>{recording ? "Recording… tap stop to send your voice note." : "Never share OTPs, PINs or passwords — not even with this assistant."}</span>
            <a href="tel:1930" className="flex items-center gap-1 text-cyber-green hover:underline">
              <PhoneCall className="h-3 w-3" /> 1930 helpline
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}