"use client";
import AuthGate from "../../components/AuthGate"; import CatalogView from "../../components/CatalogView";
export default function Page() { return <AuthGate>{({ token, user }) => <div className="glass-card"><CatalogView token={token} user={user} /></div>}</AuthGate>; }
