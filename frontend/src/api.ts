const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export async function postChat(question: string, sessionId?: string) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId }),
  });

  if (!response.ok) {
    throw new Error('Chat request failed');
  }

  return response.json();
}

export async function connectDatabase(databaseType: string) {
  const response = await fetch(`${API_BASE_URL}/database/connect?database_type=${databaseType}`);
  if (!response.ok) {
    throw new Error('Connection test failed');
  }
  return response.json();
}

export async function executeQuery(databaseType: string, query: string) {
  const response = await fetch(`${API_BASE_URL}/database/query?database_type=${databaseType}&query=${encodeURIComponent(query)}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Query execution failed');
  }
  return response.json();
}
