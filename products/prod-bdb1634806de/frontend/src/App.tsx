import { useEffect, useState } from "react";
import PublicWidget from "./pages/PublicWidget";
import OperatorLogin from "./pages/OperatorLogin";
import OperatorDashboard from "./pages/OperatorDashboard";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";

const globalStyles = `
:root {
  --bg-deep: #0a0f14;
  --surface: #111820;
  --surface-2: #18222b;
  --text: #e8eef2;
  --text-muted: #8b9aa7;
  --accent: #00d4aa;
  --accent-2: #00a3ff;
  --warning: #f5a623;
  --danger: #ff4d4f;
  --border: #263340;
  --radius-lg: 12px;
  --shadow-soft: 0 8px 24px rgba(0,0,0,0.5);
  --font-display: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background: var(--bg-deep); color: var(--text); font-family: var(--font-body); line-height:1.5; -webkit-font-smoothing: antialiased; }
h1,h2,h3,h4 { font-family: var(--font-display); line-height:1.2; }
.app-nav { background: var(--surface); border-bottom:1px solid var(--border); padding:0.75rem 1.5rem; display:flex; gap:1rem; align-items:center; position:sticky; top:0; z-index:10; }
.app-nav a { color: var(--text-muted); text-decoration:none; font-size:0.9rem; padding:0.5rem 0.75rem; border-radius:6px; transition: background 0.15s, color 0.15s; }
.app-nav a:hover, .app-nav a.active { background: var(--surface-2); color: var(--accent); }
.app-container { max-width:1200px; margin:0 auto; padding:2rem 1.5rem; }
.btn { display:inline-block; padding:0.75rem 1.5rem; border-radius:var(--radius-lg); border:1px solid var(--border); background: var(--accent); color:#0a0f14; font-weight:600; cursor:pointer; transition: all 0.2s; text-decoration:none; }
.btn:hover { filter:brightness(1.1); box-shadow: var(--shadow-soft); }
.btn-secondary { background: var(--surface-2); color: var(--text); border-color: var(--border); }
.btn-secondary:hover { background: var(--surface); border-color: var(--accent); }
.card { background: var(--surface); border:1px solid var(--border); border-radius:var(--radius-lg); padding:1.5rem; box-shadow: var(--shadow-soft); margin-bottom:1.5rem; }
.card h2 { margin-bottom:1rem; }
.grid { display:grid; gap:1.5rem; }
.grid-3 { grid-template-columns: repeat(3,1fr); }
@media (max-width:800px) { .grid-3 { grid-template-columns:1fr; } .app-nav { flex-wrap:wrap; } }
.badge { display:inline-flex; align-items:center; gap:0.5rem; padding:0.25rem 0.75rem; border-radius:999px; font-size:0.8rem; font-weight:600; }
.calm { background:#123; color:#00d4aa; }
.watch { background:#332; color:#f5a623; }
.warning { background:#432; color:#ff8c42; }
.emergency { background:#422; color:#ff4d4f; }
.unknown { background:#222; color:#8b9aa7; }
.muted { color: var(--text-muted); }
.mono { font-family: monospace; font-size:0.85em; }
`;

type Route = "widget" | "login" | "operator" | "analytics";

function App() {
  const [route, setRoute] = useState<Route>(() => {
    const hash = window.location.hash.replace(/^#\/?/, "").split("?")[0];
    if (hash.startsWith("login")) return "login";
    if (hash.startsWith("operator")) return "operator";
    if (hash.startsWith("analytics")) return "analytics";
    return "widget";
  });

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace(/^#\/?/, "").split("?")[0];
      if (hash.startsWith("login")) setRoute("login");
      else if (hash.startsWith("operator")) setRoute("operator");
      else if (hash.startsWith("analytics")) setRoute("analytics");
      else setRoute("widget");
    };
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  return (
    <>
      <style>{globalStyles}</style>
      <nav className="app-nav" aria-label="Main navigation">
        <a href="#/widget" className={route === "widget" ? "active" : ""}>Widget</a>
        <a href="#/login" className={route === "login" ? "active" : ""}>Login</a>
        <a href="#/operator" className={route === "operator" ? "active" : ""}>Operator</a>
        <a href="#/analytics" className={route === "analytics" ? "active" : ""}>Analytics</a>
      </nav>
      <div className="app-container">
        {route === "widget" && <PublicWidget />}
        {route === "login" && <OperatorLogin />}
        {route === "operator" && <OperatorDashboard />}
        {route === "analytics" && <AnalyticsDashboard />}
      </div>
    </>
  );
}

export default App;
