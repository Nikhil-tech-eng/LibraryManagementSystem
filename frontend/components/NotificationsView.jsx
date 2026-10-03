"use client";
import { useState, useEffect } from "react";
import { notificationsApi } from "../lib/apiClient";

export default function NotificationsView({ token }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    notificationsApi.list(token)
      .then(setLogs)
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {loading && <div style={{ color: "var(--text-secondary)" }}>Loading…</div>}
      <table>
        <thead>
          <tr><th>ID</th><th>Member</th><th>Type</th><th>Message</th><th>Status</th><th>Sent At</th></tr>
        </thead>
        <tbody>
          {logs.map((n) => (
            <tr key={n.id}>
              <td>{n.id}</td>
              <td>{n.member_id}</td>
              <td><span className={`badge ${n.type === "checkout" ? "badge-blue" : "badge-green"}`}>{n.type}</span></td>
              <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.message}</td>
              <td><span className={`badge ${n.status === "sent" ? "badge-green" : "badge-red"}`}>{n.status}</span></td>
              <td style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}>{n.sent_at}</td>
            </tr>
          ))}
          {logs.length === 0 && !loading && (
            <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--text-secondary)", padding: "2rem" }}>No notifications yet</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
