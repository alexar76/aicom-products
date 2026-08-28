import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
export function Share() {
    const { token = '' } = useParams();
    const q = useQuery({
        queryKey: ['public', token],
        queryFn: () => api.readPublic(token),
        enabled: !!token,
        retry: false,
    });
    if (q.isLoading)
        return _jsx("main", { className: "share-page", children: _jsx("div", { className: "skeleton", style: { height: 64, maxWidth: 720, margin: '0 auto' } }) });
    if (q.isError || !q.data) {
        return (_jsx("main", { className: "share-page", children: _jsxs("div", { className: "share-card", children: [_jsx("h1", { children: "Not available" }), _jsx("p", { children: "This handoff is either pending review, rejected, or has been removed. No draft content is shown." })] }) }));
    }
    const { handoff, workspace, verification_source } = q.data;
    return (_jsx("main", { className: "share-page", children: _jsxs("article", { className: "share-card", style: { borderLeft: `6px solid ${workspace.accent_color}` }, children: [_jsxs("div", { className: "verified-badge", role: "status", "aria-label": `Human-verified by ${workspace.name}`, children: [_jsx("svg", { width: "16", height: "16", viewBox: "0 0 24 24", "aria-hidden": "true", children: _jsx("path", { d: "M5 12l4 4 10-10", fill: "none", stroke: "currentColor", strokeWidth: "2.5", strokeLinecap: "round", strokeLinejoin: "round" }) }), "Human-verified by ", workspace.name] }), _jsxs("h1", { style: { marginTop: 16 }, children: [handoff.client_name, " \u2014 ", handoff.project_name] }), _jsxs("p", { className: "byline", children: ["Approved ", handoff.approved_at ? new Date(handoff.approved_at).toLocaleString() : '', " \u00B7 source: ", handoff.source_ai_tool, " \u00B7 review source: ", verification_source] }), _jsx("div", { className: "body", children: handoff.approved_text }), _jsxs("p", { className: "byline mono", children: ["Content hash: ", _jsx("code", { children: handoff.content_sha256 })] }), workspace.tier === 'free' && _jsx("p", { className: "footer-mark", children: "Made with Relay" })] }) }));
}
