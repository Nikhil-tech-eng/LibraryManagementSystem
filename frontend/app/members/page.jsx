"use client";
import AuthGate from "../../components/AuthGate"; import MembersView from "../../components/MembersView";
export default function Page() { return <AuthGate roles={["librarian", "admin"]}>{({ token, user }) => <div className="glass-card"><MembersView token={token} user={user} /></div>}</AuthGate>; }
