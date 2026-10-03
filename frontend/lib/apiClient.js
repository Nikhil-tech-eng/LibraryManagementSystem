/**
 * API client — thin fetch wrappers for all 4 LMS microservices.
 * In Docker/K8s, Next.js rewrites proxy to the respective service.
 * In browser dev, all calls go to localhost:3000 which rewrites them.
 */

const BASE = '';  // empty → relative URLs; rewritten by next.config.js

async function request(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

// --- Book Catalog ---
export const booksApi = {
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request('GET', `/api/books${q ? '?' + q : ''}`);
  },
  get: (id) => request('GET', `/api/books/${id}`),
  create: (data, token) => request('POST', '/api/books', data, token),
  update: (id, data, token) => request('PUT', `/api/books/${id}`, data, token),
  delete: (id, token) => request('DELETE', `/api/books/${id}`, null, token),
};

// --- User / Auth ---
export const authApi = {
  register: (data) => request('POST', '/api/users/register', data),
  login: (data) => request('POST', '/api/users/login', data),
  logout: (token) => request('POST', '/api/users/logout', null, token),
  me: (token) => request('GET', '/api/users/me', null, token),
  listUsers: (token) => request('GET', '/api/users', null, token),
};

// --- Borrowing ---
export const borrowApi = {
  request: (data, token) => request('POST', '/api/borrow/request', data, token),
  myLoans: (token) => request('GET', '/api/borrow/my-loans', null, token),
  pending: (token) => request('GET', '/api/borrow/pending', null, token),
  approve: (id, token) => request('POST', `/api/borrow/${id}/approve`, null, token),
  reject: (id, token) => request('POST', `/api/borrow/${id}/reject`, null, token),
  markReturned: (id, token) => request('POST', `/api/borrow/${id}/return`, null, token),
  active: (token) => request('GET', '/api/borrow/active', null, token),
  stats: (token) => request('GET', '/api/borrow/stats', null, token),
  dashboard: (token) => request('GET', '/api/borrow/admin/dashboard', null, token),
};

// --- Notifications ---
export const notificationsApi = {
  list: (token) => request('GET', '/api/notifications/', null, token),
};
