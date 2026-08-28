import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
export function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState(import.meta.env.VITE_DEMO_EMAIL || '');
    const [password, setPassword] = useState(import.meta.env.VITE_DEMO_PASSWORD || '');
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    async function onSubmit(e) {
        e.preventDefault();
        setError(null);
        setBusy(true);
        try {
            const r = await api.login({ email, password });
            // Capture CSRF token for subsequent mutating requests.
            const csrfRes = await api.csrf();
            setCsrfMeta(csrfRes.csrf_token);
            navigate('/inbox');
            void r;
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'login failed');
        }
        finally {
            setBusy(false);
        }
    }
    return (_jsxs("main", { className: "auth-page surface", children: [_jsx("h1", { children: "Sign in" }), _jsx("p", { children: "Welcome back to Relay." }), _jsxs("form", { className: "widget-form", onSubmit: onSubmit, children: [_jsxs("label", { children: ["Email", _jsx("input", { type: "email", value: email, onChange: (e) => setEmail(e.target.value), autoComplete: "email", required: true })] }), _jsxs("label", { children: ["Password", _jsx("input", { type: "password", value: password, onChange: (e) => setPassword(e.target.value), autoComplete: "current-password", required: true })] }), error && _jsx("p", { className: "error", role: "alert", children: error }), _jsx("button", { className: "btn", type: "submit", disabled: busy, "data-testid": "login-submit", children: busy ? 'Signing in…' : 'Sign in' })] })] }));
}
function setCsrfMeta(token) {
    let meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) {
        meta = document.createElement('meta');
        meta.name = 'csrf-token';
        document.head.appendChild(meta);
    }
    meta.content = token;
}
