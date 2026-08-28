import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, ApiError } from '../api';
export function NewHandoff() {
    const navigate = useNavigate();
    const [clientName, setClientName] = useState('');
    const [projectName, setProjectName] = useState('');
    const [sourceAiTool, setSourceAiTool] = useState('ChatGPT');
    const [draftText, setDraftText] = useState('');
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    async function onSubmit(e) {
        e.preventDefault();
        setError(null);
        setBusy(true);
        try {
            const h = await api.createHandoff({ client_name: clientName, project_name: projectName, source_ai_tool: sourceAiTool, draft_text: draftText });
            navigate(`/handoffs/${h.id}`);
        }
        catch (err) {
            if (err instanceof ApiError && err.status === 413)
                setError('Draft is too long (50,000 character limit).');
            else
                setError(err instanceof Error ? err.message : 'failed to create handoff');
        }
        finally {
            setBusy(false);
        }
    }
    return (_jsxs("main", { className: "container", style: { padding: '32px 0 64px' }, children: [_jsx("h1", { children: "New handoff" }), _jsx("p", { children: "Paste an AI draft. You will run a skeptic pass next." }), _jsxs("form", { className: "widget-form", onSubmit: onSubmit, children: [_jsxs("label", { children: ["Client name", _jsx("input", { value: clientName, onChange: (e) => setClientName(e.target.value), required: true })] }), _jsxs("label", { children: ["Project name", _jsx("input", { value: projectName, onChange: (e) => setProjectName(e.target.value), required: true })] }), _jsxs("label", { children: ["Source AI tool", _jsx("input", { value: sourceAiTool, onChange: (e) => setSourceAiTool(e.target.value), required: true })] }), _jsxs("label", { children: ["Draft text (\u2265 20 characters)", _jsx("textarea", { rows: 10, value: draftText, onChange: (e) => setDraftText(e.target.value), required: true, minLength: 20 })] }), error && _jsx("p", { className: "error", role: "alert", children: error }), _jsx("button", { className: "btn", type: "submit", disabled: busy, "data-testid": "create-handoff", children: busy ? 'Creating…' : 'Create handoff' })] })] }));
}
