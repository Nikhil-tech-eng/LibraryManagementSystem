"use client";
import AuthGate from "../../components/AuthGate"; import CirculationView from "../../components/CirculationView";
export default function Page() { return <AuthGate roles={["librarian", "admin"]}>{({ token, user }) => <CirculationView token={token} user={user} />}</AuthGate>; }
