"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "./Navbar";
export default function AuthGate({ children, roles }) {
  const router = useRouter(); const [session, setSession] = useState(null);
  useEffect(() => { const raw = window.localStorage.getItem("lms_session"); if (!raw) { router.replace("/"); return; } const parsed = JSON.parse(raw); if (roles && !roles.includes(parsed.user?.role)) { router.replace(parsed.user?.role === "member" ? "/catalog" : "/dashboard"); return; } setSession(parsed); }, [router, roles]);
  if (!session) return <main style={{ padding: "3rem", textAlign: "center" }}>Checking session…</main>;
  return <><Navbar token={session.token} user={session.user} /><main style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1rem" }}>{children({ token: session.token, user: session.user })}</main></>;
}
