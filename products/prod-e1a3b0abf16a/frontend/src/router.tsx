import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Inbox } from './pages/Inbox';
import { NewHandoff } from './pages/NewHandoff';
import { HandoffDetail } from './pages/HandoffDetail';
import { Branding } from './pages/Branding';
import { Share } from './pages/Share';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/inbox" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/inbox" element={<Inbox />} />
      <Route path="/handoffs/new" element={<NewHandoff />} />
      <Route path="/handoffs/:id" element={<HandoffDetail />} />
      <Route path="/settings/branding" element={<Branding />} />
      <Route path="/share/:token" element={<Share />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

function NotFound() {
  return (
    <main className="not-found">
      <h1>Not available</h1>
      <p>This handoff either does not exist, has not been approved, or has been removed.</p>
    </main>
  );
}
