import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, ApiError } from '../api';
export function Branding() {
    const qc = useQueryClient();
    const ws = useQuery({ queryKey: ['branding'], queryFn: () => api.getBranding(), retry: false });
    const [name, setName] = useState('');
    const [logoUrl, setLogoUrl] = useState('');
    const [accent, setAccent] = useState('#8a1c2b');
    const [error, setError] = useState(null);
    useEffect(() => {
        if (ws.data) {
            setName(ws.data.name || '');
            setLogoUrl(ws.data.logo_url || '');
            setAccent(ws.data.accent_color || '#8a1c2b');
        }
    }, [ws.data]);
    const save = useMutation({
        mutationFn: () => api.putBranding({ name, logo_url: logoUrl, accent_color: accent }),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['branding'] });
            setError(null);
        },
        onError: (e) => setError(e instanceof Error ? e.message : 'save failed'),
    });
    if (ws.isLoading) {
        return (_jsx("main", { className: "page-shell", children: _jsx("div", { className: "skeleton", style: { height: 64 } }) }));
    }
    if (ws.isError) {
        const status = ws.error instanceof ApiError ? ws.error.status : 0;
        return (_jsxs("main", { className: "page-shell", style: { padding: '32px 0 64px' }, children: [_jsx("h1", { children: "Branding" }), _jsx("p", { className: "error", role: "alert", children: status === 401
                        ? 'Sign in to edit workspace branding.'
                        : ws.error instanceof Error
                            ? ws.error.message
                            : 'Could not load branding.' }), status === 401 && (_jsx("p", { children: _jsx(Link, { to: "/login", children: "Sign in" }) }))] }));
    }
    return (_jsxs("main", { className: "page-shell", style: { padding: '32px 0 64px' }, children: [_jsx("h1", { children: "Branding" }), _jsx("p", { children: "Customize how your share page and embed badge look to clients." }), _jsxs("form", { className: "widget-form", onSubmit: (e) => {
                    e.preventDefault();
                    save.mutate(undefined);
                }, children: [_jsxs("label", { children: ["Workspace name", _jsx("input", { value: name, onChange: (e) => setName(e.target.value) })] }), _jsxs("label", { children: ["Logo URL (https only)", _jsx("input", { value: logoUrl, onChange: (e) => setLogoUrl(e.target.value), placeholder: "https://" })] }), _jsxs("label", { children: ["Accent color", _jsx("input", { value: accent, onChange: (e) => setAccent(e.target.value) })] }), error && (_jsx("p", { className: "error", role: "alert", children: error })), _jsx("button", { className: "btn", type: "submit", disabled: save.isPending, children: save.isPending ? 'Saving…' : 'Save' })] })] }));
}
