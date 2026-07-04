const API_BASE = ''

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`)
    const data = await res.json()
    return {
      connected: data.llm_connected,
      indexed: data.indexed,
      loading: false,
    }
  } catch {
    return { connected: false, indexed: false, loading: false }
  }
}

export async function sendQuery(question, history = []) {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function sendChat(message, history = []) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export async function uploadFiles(files) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Upload failed (${res.status})`)
  }
  return res.json()
}

export async function getProcessingStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/processing`)
    return await res.json()
  } catch {
    return { active: false, status: '', progress: 0 }
  }
}

export async function getModels() {
  const res = await fetch(`${API_BASE}/api/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  return res.json()
}

export async function switchModel(path) {
  const res = await fetch(`${API_BASE}/api/models/switch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Switch failed')
  }
  return res.json()
}
