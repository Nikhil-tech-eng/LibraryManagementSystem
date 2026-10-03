"use client";
import AuthGate from "../../components/AuthGate"; import DashboardView from "../../components/DashboardView";
export default function Page() { return <AuthGate roles={["librarian", "admin"]}>{({ token }) => <DashboardView token={token} />}</AuthGate>; }
