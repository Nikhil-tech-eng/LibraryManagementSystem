"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { BookOpen, Clock3, Library, AlertTriangle, Users } from "lucide-react";
import { borrowApi } from "../lib/apiClient";
export default function DashboardView({ token }) {
  const [data, setData] = useState(null); const [error, setError] = useState("");
  useEffect(() => { borrowApi.dashboard(token).then(setData).catch((e) => setError(e.message)); }, [token]);
  if (error) return <div style={{ color: "var(--accent-red)" }}>{error}</div>;
  if (!data) return <div>Loading dashboard…</div>;
  const cards = [["Total Books", data.total_books, BookOpen, "/catalog"], ["Pending Requests", data.pending_requests, Clock3, "/circulation"], ["Active Loans", data.active_issued_loans, Library, "/circulation"], ["Overdue Books", data.overdue_loans, AlertTriangle, "/circulation"], ["Members", data.total_members, Users, "/members"]];
  return <div><header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}><div><div style={{ fontSize: "1.7rem", fontWeight: 800 }}>◈ Library Command Center</div><p style={{ color: "var(--text-secondary)" }}>Operations overview for staff</p></div><span className="badge badge-purple">Admin workspace</span></header><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: "1rem", marginBottom: "1.5rem" }}>{cards.map(([label, value, Icon, href]) => <Link key={label} href={href} className="glass-card" style={{ textDecoration: "none", color: "var(--text-primary)" }}><Icon size={20} color="var(--accent-blue)" /><div style={{ fontSize: "2rem", fontWeight: 800, marginTop: ".75rem" }}>{value}</div><div style={{ color: "var(--text-secondary)" }}>{label}</div></Link>)}</div><div className="glass-card"><h3 style={{ marginBottom: "1rem" }}>Recent Circulation Activity</h3><table><thead><tr><th>Member</th><th>Book</th><th>Status</th><th>Date</th></tr></thead><tbody>{data.recent_activity.map((a) => <tr key={a.id}><td>{a.member_name}</td><td>{a.book_title}</td><td><span className="badge badge-blue">{a.status}</span></td><td>{a.event_date?.slice(0, 10)}</td></tr>)}</tbody></table></div></div>;
}
