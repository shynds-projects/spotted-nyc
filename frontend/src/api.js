const API_BASE = 'https://spotted-nyc-production.up.railway.app'

export function apiFetch(path) {
  return fetch(`${API_BASE}${path}`).then((res) => res.json())
}
