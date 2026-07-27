export const BACKEND_URL = 'http://127.0.0.1:8000'

export function getBackendUrl() {
  return BACKEND_URL
}

function getAuthHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function login(email, password) {
  const response = await fetch(`${BACKEND_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  if (!response.ok) throw new Error('Invalid credentials')
  return response.json()
}

export async function fetchProfile(token) {
  const response = await fetch(`${BACKEND_URL}/users/me`, {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Unable to load profile')
  return response.json()
}

export async function createResource(token, path, body) {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Create failed')
  }
  return response.json()
}

export async function listResources(token, path, query = '') {
  const url = new URL(`${BACKEND_URL}/api/${path}`)
  if (query) url.search = query
  const response = await fetch(url.toString(), { headers: { ...getAuthHeaders(token) } })
  if (!response.ok) throw new Error('List failed')
  return response.json()
}

export async function getResource(token, path, id) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, { headers: { ...getAuthHeaders(token) } })
  if (!response.ok) throw new Error('Fetch failed')
  return response.json()
}

export async function updateResource(token, path, id, body) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders(token) },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Update failed')
  }
  return response.json()
}

export async function deleteResource(token, path, id) {
  const response = await fetch(`${BACKEND_URL}/api/${path}/${id}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Delete failed')
  return null
}

export async function uploadFile(token, path, file, fieldName = 'file') {
  const formData = new FormData()
  formData.append(fieldName, file)
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    method: 'POST',
    headers: { ...getAuthHeaders(token) },
    body: formData,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Upload failed')
  }
  return response.json()
}

export async function downloadFile(token, path, filename = 'download') {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Download failed')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
  return true
}

export async function fetchText(token, path) {
  const response = await fetch(`${BACKEND_URL}/api/${path}`, {
    headers: { ...getAuthHeaders(token) },
  })
  if (!response.ok) throw new Error('Fetch failed')
  return response.text()
}
