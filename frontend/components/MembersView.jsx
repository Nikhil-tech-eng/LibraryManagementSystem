"use client";
import { useState, useEffect } from "react";
import { authApi, borrowApi } from "../lib/apiClient";

export default function MembersView({ token, user }) {
  const [members, setMembers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    if (["librarian", "admin"].includes(user?.role)) {
      authApi.listUsers(token).then(setMembers).catch((e) => setError(e.message));
      borrowApi.stats(token).then(setStats).catch(() => {});
    }
  }, [token, user]);

  if (!token) return <p style={{ color: "var(--text-secondary)" }}>Please log in.</p>;
  if (!["librarian", "admin"].includes(user?.role)) return <p style={{ color: "var(--text-secondary)" }}>Staff access only.</p>;

  return (
    <div>
      {stats && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {[
            { label: "Active Loans", value: stats.total_active, color: "var(--accent-blue)" },
            { label: "Overdue", value: stats.total_overdue, color: "var(--accent-red)" },
            { label: "Returned", value: stats.total_returned, color: "var(--accent-green)" },
          ].map(({ label, value, color }) => (
            <div key={label} className="glass-card" style={{ flex: 1, minWidth: 140, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", fontWeight: 700, color }}>{value}</div>
              <div style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}>{label}</div>
            </div>
          ))}
        </div>
      )}
      {error && <div style={{ color: "var(--accent-red)", marginBottom: "1rem" }}>{error}</div>}
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Member Since</th></tr></thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td>
              <td style={{ fontWeight: 500 }}>{m.name}</td>
              <td style={{ color: "var(--text-secondary)" }}>{m.email}</td>
              <td><span className={`badge ${m.role === "librarian" ? "badge-purple" : "badge-blue"}`}>{m.role}</span></td>
              <td style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}>{m.membership_start}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
