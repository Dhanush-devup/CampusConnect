import { useEffect, useRef } from "react";
import { Application } from "../api/types";

const POLL_INTERVAL_MS = 3000;

/**
 * Re-runs `refresh` every few seconds while any application's ATS score is still pending.
 */
export function usePendingScoreRefresh(applications: Application[], refresh: () => void) {
  const refreshRef = useRef(refresh);
  useEffect(() => {
    refreshRef.current = refresh;
  });
  const hasPending = applications.some((app) => app.ats_status === "pending");

  useEffect(() => {
    if (!hasPending) return;
    const id = window.setInterval(() => refreshRef.current(), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [hasPending]);
}
