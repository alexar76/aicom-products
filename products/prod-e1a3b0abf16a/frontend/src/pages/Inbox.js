import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
export function Inbox() {
    const [tab, setTab] = useState('pending');
    const { data, isLoading, error } = useQuery({
        queryKey: ['handoffs', tab],
        queryFn: () => api.listHandoffs(tab),
    });
    return (_jsxs("main", { className: "inbox container", children: [_jsxs("header", { className: "app-nav", style: { margin: '-32px -24px 24px', borderRadius: 0 }, children: [_jsx(Link, { className: "brand", to: "/inbox", children: "Relay" }), _jsxs("nav", { className: "links", children: [_jsx(Link, { to: "/handoffs/new", children: "New handoff" }), _jsx(Link, { to: "/settings/branding", children: "Branding" })] })] }), _jsx("h1", { children: "Inbox" }), _jsx("p", { children: "Pending, approved, and rejected handoffs in your workspace." }), _jsx("div", { className: "tabs", role: "tablist", children: ['pending', 'approved', 'rejected'].map((s) => (_jsxs("button", { role: "tab", "aria-selected": tab === s, className: "tab", onClick: () => setTab(s), children: [s.charAt(0).toUpperCase() + s.slice(1), " (", data?.counts[s] ?? 0, ")"] }, s))) }), isLoading && _jsx("div", { className: "skeleton", style: { height: 64 } }), error && _jsx("p", { className: "error", children: "Failed to load handoffs." }), data && data.items.length === 0 && (_jsxs("div", { className: "surface empty", children: [_jsx("p", { children: "No handoffs here yet." }), _jsx(Link, { to: "/handoffs/new", className: "btn btn--secondary", children: "Start a handoff" })] })), data && data.items.length > 0 && (_jsx("div", { className: "grid", children: data.items.map((h) => (_jsxs(Link, { to: `/handoffs/${h.id}`, className: "card surface", style: { color: 'inherit', borderBottom: 'none' }, children: [_jsx("h3", { children: h.client_name }), _jsxs("div", { className: "meta", children: [h.project_name, " \u00B7 ", h.source_ai_tool] }), _jsx("div", { className: "meta", style: { marginTop: 8 }, children: new Date(h.created_at).toLocaleString() })] }, h.id))) }))] }));
}
