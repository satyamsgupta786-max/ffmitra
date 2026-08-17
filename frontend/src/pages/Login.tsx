import { useState } from "react";
import { motion } from "framer-motion";
import { LogIn, Eye, EyeOff, ShieldCheck, KeyRound } from "lucide-react";
import { Logo } from "@/components/Logo";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";

const DEMO_EMAIL = "admin@ffmitra.local";
const DEMO_PASSWORD = "Analyst@2026";

export function Login() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState(DEMO_EMAIL);
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await signIn(email, password);
      navigate("/");
    } catch (err: any) {
      setError(err.message ?? "sign in failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative flex h-screen items-center justify-center overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute left-1/4 top-1/4 h-72 w-72 animate-pulse rounded-full bg-cyber-cyan/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-72 w-72 animate-pulse rounded-full bg-cyber-violet/10 blur-3xl" style={{ animationDelay: "1.5s" }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        <div className="mb-8 flex justify-center">
          <Logo size={44} />
        </div>

        <form onSubmit={submit} className="panel p-8">
          <div className="mb-6 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.3em] text-slate-500">
            <ShieldCheck className="h-3.5 w-3.5 text-cyber-green" /> secure analyst access
          </div>

          <label className="label">Email</label>
          <div className="relative mb-4">
            <KeyRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="email"
              className="input pl-9"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@ffmitra.local"
              autoComplete="username"
            />
          </div>

          <label className="label">Password</label>
          <div className="relative mb-5">
            <input
              type={show ? "text" : "password"}
              className="input pr-10"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShow((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyber-cyan"
            >
              {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 rounded-md border border-cyber-red/30 bg-cyber-red/10 px-3 py-2 font-mono text-xs text-cyber-red"
            >
              {error}
            </motion.div>
          )}

          <button type="submit" className="btn-primary w-full" disabled={busy}>
            <LogIn className="h-4 w-4" />
            {busy ? "Authenticating…" : "Enter Command Center"}
          </button>

          <div className="mt-5 rounded-md border border-cyber-cyan/10 bg-ink-850 px-3 py-2.5 font-mono text-[10.5px] text-slate-500">
            <div className="mb-1 text-slate-400">DEMO CREDENTIALS</div>
            <div className="flex justify-between"><span>{DEMO_EMAIL}</span><span className="text-cyber-cyan">{DEMO_PASSWORD}</span></div>
          </div>
        </form>

        <p className="mt-6 text-center font-mono text-[10px] uppercase tracking-[0.25em] text-slate-600">
          FFMitra · AI Financial Fraud Detection & Prevention · KAVACH 2023
        </p>
      </motion.div>
    </div>
  );
}