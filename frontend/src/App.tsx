import { Link, Route, Routes } from 'react-router-dom';

function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', padding: 24 }}>
      <header style={{ marginBottom: 24 }}>
        <h1>AI Data Platform</h1>
        <p>Enterprise analytics copilot with LangGraph orchestration.</p>
        <nav style={{ display: 'flex', gap: 12 }}>
          <Link to="/">Chat</Link>
          <Link to="/connections">Connections</Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/connections" element={<ConnectionsPage />} />
      </Routes>
    </div>
  );
}

function ChatPage() {
  return <div>Chat experience coming soon.</div>;
}

function ConnectionsPage() {
  return <div>Database connection management coming soon.</div>;
}

export default App;
