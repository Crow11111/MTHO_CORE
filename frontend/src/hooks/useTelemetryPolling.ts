import { useState, useEffect, useRef, useCallback } from 'react';

export type WatchdogData = {
  latency_ms: number;
  git_status: string;
  mode: string;
  timestamp: number;
};

export type TelemetryData = {
  watchdog: WatchdogData;
  friction_violations: number;
  event_bus_connected: boolean;
  api_uptime_s: number;
  shell?: {
    z_vector: number;
    total_tokens: number;
    call_count: number;
    max_iterations: number;
    token_kill_threshold: number;
  };
};

type UseTelemetryOptions = {
  apiBase: string;
  intervalMs?: number;
  enabled?: boolean;
};

export function useTelemetryPolling({
  apiBase,
  intervalMs = 5000,
  enabled = true,
}: UseTelemetryOptions) {
  const [data, setData] = useState<TelemetryData | null>(null);
  const [connected, setConnected] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchTelemetry = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/api/core/telemetry`, {
        signal: AbortSignal.timeout(4000),
      });
      if (res.ok) {
        const json: TelemetryData = await res.json();
        setData(json);
        setConnected(true);
      } else {
        setConnected(false);
      }
    } catch {
      setConnected(false);
    }
  }, [apiBase]);

  useEffect(() => {
    if (!enabled) {
      setConnected(false);
      return;
    }

    fetchTelemetry();
    timerRef.current = setInterval(fetchTelemetry, intervalMs);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [enabled, intervalMs, fetchTelemetry]);

  return { data, connected };
}
