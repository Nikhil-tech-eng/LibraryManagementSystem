"use client";
import AuthGate from "../../components/AuthGate"; import CirculationView from "../../components/CirculationView";
export default function Page() { return <AuthGate roles={["member"]}>{({ token, user }) => <div className="glass-card"><CirculationView token={token} user={user} memberMode /></div>}</AuthGate>; }
