"use client";
import AuthGate from "../../components/AuthGate"; import NotificationsView from "../../components/NotificationsView";
export default function Page() { return <AuthGate>{({ token }) => <div className="glass-card"><NotificationsView token={token} /></div>}</AuthGate>; }
