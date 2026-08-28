import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
export function Signup() {
    const navigate = useNavigate();
    const [email, setEmail] = useState(import.meta.env.VITE_DEMO_EMAIL || '');
    const [password, setPassword] = useState(import.meta.env.VITE_DEMO_PASSWORD || '');
    const [workspace, setWorkspace] = useState('My Studio');
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    async function onSubmit(e) {
        e.preventDefault();
        setError(null);
        setBusy(true);
        try {
            await api.signup({ email, password, workspace_name: workspace });
            const csrf = await api.csrf();
            let meta = document.querySelector('meta[name="csrf-token"]');
            if (!meta) {
                meta = document.createElement('meta');
                meta.name = 'csrf-token';
                document.head.appendChild(meta);
            }
            meta.content = csrf.csrf_token;
            navigate('/inbox');
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'signup failed');
        }
        finally {
            setBusy(false);
        }
    }
    return (_jsxs("main", { className: "auth-page surface", children: [_jsx("h1", { children: "Create your workspace" }), _jsx("p", { children: "One workspace per team on the free tier." }), _jsxs("form", { className: "widget-form", onSubmit: onSubmit, children: [_jsxs("label", { children: ["Workspace name", _jsx("input", { value: workspace, onChange: (e) => setWorkspace(e.target.value), required: true })] }), _jsxs("label", { children: ["Email", _jsx("input", { type: "email", value: email, onChange: (e) => setEmail(e.target.value), required: true })] }), _jsxs("label", { children: ["Password (\u2265 10 characters)", _jsx("input", { type: "password", value: password, onChange: (e) => setPassword(e.target.value), required: true, minLength: 10 })] }), error && _jsx("p", { className: "error", role: "alert", children: error }), _jsx("button", { className: "btn", type: "submit", disabled: busy, "data-testid": "signup-submit", children: busy ? 'Creating…' : 'Create workspace' })] })] }));
}
