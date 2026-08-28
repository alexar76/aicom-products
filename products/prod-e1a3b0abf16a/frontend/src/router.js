import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Inbox } from './pages/Inbox';
import { NewHandoff } from './pages/NewHandoff';
import { HandoffDetail } from './pages/HandoffDetail';
import { Branding } from './pages/Branding';
import { Share } from './pages/Share';
export function App() {
    return (_jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(Navigate, { to: "/inbox", replace: true }) }), _jsx(Route, { path: "/login", element: _jsx(Login, {}) }), _jsx(Route, { path: "/signup", element: _jsx(Signup, {}) }), _jsx(Route, { path: "/inbox", element: _jsx(Inbox, {}) }), _jsx(Route, { path: "/handoffs/new", element: _jsx(NewHandoff, {}) }), _jsx(Route, { path: "/handoffs/:id", element: _jsx(HandoffDetail, {}) }), _jsx(Route, { path: "/settings/branding", element: _jsx(Branding, {}) }), _jsx(Route, { path: "/share/:token", element: _jsx(Share, {}) }), _jsx(Route, { path: "*", element: _jsx(NotFound, {}) })] }));
}
function NotFound() {
    return (_jsxs("main", { className: "not-found", children: [_jsx("h1", { children: "Not available" }), _jsx("p", { children: "This handoff either does not exist, has not been approved, or has been removed." })] }));
}
