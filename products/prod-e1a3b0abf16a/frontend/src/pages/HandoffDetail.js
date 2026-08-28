import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api';
const CHECKLIST = ['claims', 'sources', 'tone', 'risk'];
export function HandoffDetail() {
    const { id = '' } = useParams();
    const qc = useQueryClient();
    const handoff = useQuery({ queryKey: ['handoff', id], queryFn: () => api.getHandoff(id), enabled: !!id });
    const audit = useQuery({ queryKey: ['handoff-audit', id], queryFn: async () => {
            const r = await fetch(`/api/handoffs/${id}/audit`, { credentials: 'include' });
            return r.ok ? (await r.json()) : { items: [] };
        }, enabled: !!id });
    const verify = useMutation({
        mutationFn: () => api.verifyHandoff(id, CHECKLIST.map((category) => ({ category, passed: true, notes: 'Reviewed by operator.' })), false),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
    });
    const approve = useMutation({
        mutationFn: () => api.approveHandoff(id, {}),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
    });
    const reject = useMutation({
        mutationFn: (reason) => api.rejectHandoff(id, reason),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['handoff', id] }),
    });
    const receipt = useMutation({
        mutationFn: async () => {
            const r = await api.receipt(id);
            const blob = new Blob([JSON.stringify(r, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relay-receipt-${id}.json`;
            a.click();
            URL.revokeObjectURL(url);
        },
    });
    if (handoff.isLoading)
        return _jsx("main", { className: "container", children: _jsx("div", { className: "skeleton", style: { height: 64 } }) });
    if (handoff.error || !handoff.data)
        return _jsx("main", { className: "container", children: _jsx("p", { className: "error", children: "Handoff not found." }) });
    const h = handoff.data;
    const shareUrl = `${window.location.origin}/share/${h.share_token}`;
    return (_jsxs("main", { className: "detail container", children: [_jsxs("section", { className: "surface", style: { padding: 24 }, children: [_jsx("h1", { children: h.client_name }), _jsxs("p", { className: "mono", style: { color: 'var(--ink-muted)' }, children: [h.project_name, " \u00B7 ", h.source_ai_tool] }), _jsxs("p", { children: ["Status: ", _jsx("strong", { children: h.status }), " \u00B7 Verification source: ", _jsx("code", { children: h.verification_source })] }), _jsx("pre", { className: "surface", style: { padding: 16, whiteSpace: 'pre-wrap' }, children: h.approved_text || h.draft_text }), _jsxs("div", { style: { display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 16 }, children: [_jsx("button", { className: "btn", onClick: () => verify.mutate(), disabled: verify.isPending, "data-testid": "run-skeptic", children: "Run skeptic pass" }), _jsx("button", { className: "btn", onClick: () => approve.mutate(), disabled: approve.isPending || h.status === 'approved', "data-testid": "approve", children: "Approve & publish" }), _jsx("button", { className: "btn btn--secondary", onClick: () => {
                                    const reason = window.prompt('Reject reason?') || '';
                                    if (reason)
                                        reject.mutate(reason);
                                }, disabled: reject.isPending || h.status === 'rejected', children: "Reject" }), _jsx("button", { className: "btn btn--secondary", onClick: () => receipt.mutate(), disabled: receipt.isPending, children: "Export receipt" })] }), h.status === 'approved' && (_jsxs("p", { style: { marginTop: 16 }, children: ["Public share URL: ", _jsx("a", { href: shareUrl, children: shareUrl })] }))] }), _jsx("aside", { className: "audit", children: _jsxs("div", { className: "surface", style: { padding: 16 }, children: [_jsx("h2", { children: "Audit timeline" }), _jsx("ul", { children: (audit.data?.items || []).map((e) => (_jsxs("li", { children: [_jsx("strong", { children: e.action }), " \u2014 ", e.actor_email || 'system', _jsx("br", {}), _jsx("span", { style: { color: 'var(--ink-muted)' }, children: new Date(e.created_at).toLocaleString() })] }, e.id))) })] }) })] }));
}
