"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "../lib/apiClient";

export default function Navbar({ token, user }) {
  const router = useRouter();
  const isMember = user?.role === "member";
  const links = isMember ? [["Catalog", "/catalog"], ["My Loans", "/my-loans"], ["Notifications", "/notifications"]] : [["Dashboard", "/dashboard"], ["Catalog", "/catalog"], ["Circulation", "/circulation"], ["Members", "/members"], ["Notifications", "/notifications"]];
  async function logout() { try { await authApi.logout(token); } catch {} window.localStorage.removeItem("lms_session"); router.replace("/"); }
  return <nav style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "1rem 2rem", background: "var(--bg-glass)", borderBottom: "1px solid var(--border-glass)", backdropFilter: "blur(16px)", flexWrap: "wrap" }}>
    <Link href={isMember ? "/catalog" : "/dashboard"} style={{ fontWeight: 700, fontSize: "1.1rem", marginRight: "auto", color: "var(--text-primary)", textDecoration: "none" }}>📚 LMS Portal</Link>
    <div style={{ display: "flex", gap: ".35rem", flexWrap: "wrap" }}>{links.map(([label, href]) => <Link key={href} href={href} className="btn btn-ghost">{label}</Link>)}</div>
    <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}><span style={{ color: "var(--text-secondary)", fontSize: ".875rem" }}>{user?.name} <span className="badge badge-blue">{user?.role}</span></span><button onClick={logout} className="btn btn-ghost">Logout</button></div>
  </nav>;
}
