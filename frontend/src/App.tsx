import { useState, type FormEvent } from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import { connectDatabase, executeQuery, postChat } from './api';

function App() {
  console.log('[frontend] App component rendered');
  return (
    <div style={{ fontFamily: 'sans-serif', padding: 24, maxWidth: 960, margin: '0 auto' }}>
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
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sql, setSql] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await postChat(question);
      setAnswer(result.answer);
      setSql(result.sql ?? null);
    } catch {
      setError('Unable to reach the backend. Make sure the API is running.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask for insights from your data"
          rows={4}
          style={{ padding: 12, borderRadius: 8 }}
        />
        <button type="submit" disabled={loading} style={{ width: 140, padding: 10, borderRadius: 8 }}>
          {loading ? 'Thinking…' : 'Ask platform'}
        </button>
      </form>

      {error ? <p style={{ color: 'tomato' }}>{error}</p> : null}

      {answer ? (
        <div style={{ marginTop: 24, padding: 16, background: '#111827', borderRadius: 12 }}>
          <h3>Answer</h3>
          <p>{answer}</p>
          {sql ? (
            <>
              <h3>Generated SQL</h3>
              <pre style={{ whiteSpace: 'pre-wrap' }}>{sql}</pre>
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function ConnectionsPage() {
  const [databaseType, setDatabaseType] = useState('mysql');
  const [query, setQuery] = useState('SELECT 1 AS value');
  const [status, setStatus] = useState('');
  const [rows, setRows] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleConnect() {
    setLoading(true);
    setStatus('');
    try {
      const result = await connectDatabase(databaseType);
      setStatus(result.connected ? 'Connection successful' : 'Connection failed');
    } catch {
      setStatus('Connection test failed');
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery() {
    setLoading(true);
    setStatus('');
    try {
      const result = await executeQuery(databaseType, query);
      setRows(result.rows ?? []);
      setStatus('Query executed');
    } catch {
      setStatus('Query execution failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div style={{ display: 'grid', gap: 8 }}>
        <label>
          Database type
          <select value={databaseType} onChange={(event) => setDatabaseType(event.target.value)} style={{ display: 'block', marginTop: 4, padding: 8 }}>
            <option value="mysql">MySQL</option>
            <option value="postgres">PostgreSQL</option>
            <option value="sqlite">SQLite</option>
          </select>
        </label>
        <button onClick={handleConnect} disabled={loading} style={{ width: 180, padding: 10, borderRadius: 8 }}>
          Test connection
        </button>
      </div>

      <div style={{ display: 'grid', gap: 8 }}>
        <label>
          Query
          <textarea value={query} onChange={(event) => setQuery(event.target.value)} rows={4} style={{ display: 'block', width: '100%', marginTop: 4, padding: 8 }} />
        </label>
        <button onClick={handleQuery} disabled={loading} style={{ width: 180, padding: 10, borderRadius: 8 }}>
          Run query
        </button>
      </div>

      {status ? <p>{status}</p> : null}
      {rows.length ? <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(rows, null, 2)}</pre> : null}
    </div>
  );
}

export default App;
