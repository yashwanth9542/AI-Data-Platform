const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
console.log('[frontend] API base URL:', API_BASE_URL);

export async function postChat(question: string, sessionId?: string) {
  console.log('[frontend] postChat called with question:', question, 'sessionId:', sessionId);
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId }),
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(error);

    throw new Error(error.detail);
}

  const data = await response.json();
  console.log('[frontend] postChat response data:', data);
  return data;
}

export async function connectDatabase(databaseType: string) {
  console.log('[frontend] connectDatabase called for type:', databaseType);
  const response = await fetch(`${API_BASE_URL}/database/connect?database_type=${databaseType}`);
  if (!response.ok) {
    console.error('[frontend] connectDatabase failed with status:', response.status);
    throw new Error('Connection test failed');
  }
  const data = await response.json();
  console.log('[frontend] connectDatabase response:', data);
  return data;
}

export async function executeQuery(databaseType: string, query: string) {
  console.log('[frontend] executeQuery called for type:', databaseType, 'query:', query);
  const response = await fetch(`${API_BASE_URL}/database/query?database_type=${databaseType}&query=${encodeURIComponent(query)}`, {
    method: 'POST',
  });
  if (!response.ok) {
    console.error('[frontend] executeQuery failed with status:', response.status);
    throw new Error('Query execution failed');
  }
  const data = await response.json();
  console.log('[frontend] executeQuery response:', data);
  return data;
}
