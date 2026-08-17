import { useEffect, useRef, useState } from "react";
import { subscribeToAlerts, subscribeToTransactions } from "@/lib/supabase";

type StreamItem = {
  kind: "txn" | "alert";
  ts: number;
  data: any;
};

export function useRealtimeStream(limit = 60) {
  const [items, setItems] = useState<StreamItem[]>([]);
  const [alertPulse, setAlertPulse] = useState<number>(0);
  const buffer = useRef<StreamItem[]>([]);

  useEffect(() => {
    const flush = () => {
      if (buffer.current.length === 0) return;
      const batch = [...buffer.current];
      buffer.current = [];
      setItems((prev) => [...batch, ...prev].slice(0, limit));
    };
    const interval = setInterval(flush, 350);

    const txnSub = subscribeToTransactions((newRow) => {
      buffer.current.push({ kind: "txn", ts: Date.now(), data: newRow });
    });
    const alertSub = subscribeToAlerts((newRow) => {
      buffer.current.push({ kind: "alert", ts: Date.now(), data: newRow });
      setAlertPulse((n) => n + 1);
    });

    return () => {
      clearInterval(interval);
      txnSub.unsubscribe();
      alertSub.unsubscribe();
    };
  }, [limit]);

  return { items, alertPulse, clear: () => setItems([]) };
}