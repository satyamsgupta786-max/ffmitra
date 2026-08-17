import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL ?? "https://ctvfigqlxdakrnoyujrl.supabase.co";
const SUPABASE_PUBLISHABLE_KEY =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  "sb_publishable_yhmSlpWRkoZ88hjrmD42cQ_q64cJwep";

export const supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

export function subscribeToTransactions(callback: (payload: any) => void) {
  return supabase
    .channel("ffmitra-txn-stream")
    .on(
      "postgres_changes",
      { event: "INSERT", schema: "public", table: "transactions" },
      (payload) => callback(payload.new)
    )
    .subscribe();
}

export function subscribeToAlerts(callback: (payload: any) => void) {
  return supabase
    .channel("ffmitra-alert-stream")
    .on(
      "postgres_changes",
      { event: "INSERT", schema: "public", table: "alerts" },
      (payload) => callback(payload.new)
    )
    .subscribe();
}