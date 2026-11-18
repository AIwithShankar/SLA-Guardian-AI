import { supabase } from "./supabase";

const baseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export async function predictTicket(ticketId) {
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();
  if (sessionError || !session?.access_token) throw new Error("Session expired. Please sign in again.");

  const response = await fetch(`${baseUrl}/api/v1/tickets/${encodeURIComponent(ticketId)}/predict`, {
    method: "POST",
    headers: { Authorization: `Bearer ${session.access_token}` },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : `Prediction failed (HTTP ${response.status}).`;
    throw new Error(detail);
  }
  return payload;
}
