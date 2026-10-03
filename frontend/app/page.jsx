"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../lib/apiClient";

export default function HomePage() {
  const router = useRouter();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  useEffect(() => { const raw = window.localStorage.getItem("lms_session"); if (raw) router.replace(JSON.parse(raw).user?.role === "member" ? "/catalog" : "/dashboard"); }, [router]);
  async function submit(event) {
    event.preventDefault(); setError(""); setLoading(true);
    try {
      if (mode === "register") await authApi.register({ ...form, role: "member" });
      const result = await authApi.login({ email: form.email, password: form.password });
      const user = await authApi.me(result.access_token);
      window.localStorage.setItem("lms_session", JSON.stringify({ token: result.access_token, user }));
      router.replace(user.role === "member" ? "/catalog" : "/dashboard");
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }
  return <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "1rem" }}><section className="glass-card" style={{ width: "100%", maxWidth: 430 }}>
    <div style={{ marginBottom: "1.5rem" }}><div style={{ fontSize: "1.5rem", fontWeight: 800 }}>📚 LMS Portal</div><p style={{ color: "var(--text-secondary)", marginTop: ".5rem" }}>{mode === "login" ? "Sign in to continue to your library workspace." : "Create a member account to request books."}</p></div>
    <form onSubmit={submit} style={{ display: "grid", gap: ".85rem" }}>{mode === "register" && <input placeholder="Full name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />}<input type="email" placeholder="Email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /><input type="password" placeholder="Password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />{error && <div style={{ color: "var(--accent-red)" }}>{error}</div>}<button className="btn btn-primary" type="submit" disabled={loading}>{loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}</button></form>
    <button className="btn btn-ghost" style={{ marginTop: "1rem", width: "100%" }} onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>{mode === "login" ? "New member? Register" : "Already registered? Sign in"}</button>
  </section></main>;
}
