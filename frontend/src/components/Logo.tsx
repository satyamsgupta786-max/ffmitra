export function Logo({ size = 34, withText = true }: { size?: number; withText?: boolean }) {
  return (
    <div className="flex items-center gap-2.5 select-none">
      <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-hidden>
        <defs>
          <linearGradient id="ffg" x1="0" y1="0" x2="48" y2="48">
            <stop offset="0%" stopColor="#00E5FF" />
            <stop offset="100%" stopColor="#7C5CFF" />
          </linearGradient>
        </defs>
        <path
          d="M24 3 42 10v12c0 11.5-7.6 19.6-18 23C13.6 41.6 6 33.5 6 22V10L24 3Z"
          stroke="url(#ffg)"
          strokeWidth="2.5"
          fill="rgba(0,229,255,0.05)"
        />
        <path
          d="M24 13c-5 4.5-7.5 8.5-7.5 12.5 0 3.5 2 6.5 5 8 1-3 2.5-4.5 2.5-7 0-1.6-.5-3-.5-3 1 1 1.5 2 1.5 3 0 2.5 1.5 4.5 2.5 7 3-1.5 5-4.5 5-8C31.5 21.5 29 17.5 24 13Z"
          fill="#00E5FF"
        />
        <circle cx="24" cy="26" r="1.6" fill="#0A0F1E" />
      </svg>
      {withText && (
        <div className="leading-none">
          <div className="font-display text-lg font-bold tracking-[0.12em] text-slate-100">
            FFMITRA
          </div>
          <div className="mt-0.5 font-mono text-[9.5px] uppercase tracking-[0.28em] text-cyber-cyan/70">
            Fraud Intelligence
          </div>
        </div>
      )}
    </div>
  );
}