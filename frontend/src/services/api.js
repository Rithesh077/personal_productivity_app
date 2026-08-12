/**
 * API service — all endpoint definitions.
 *
 * Every function returns a promise. Errors throw with
 * status and message for the caller to handle.
 */

const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (res.status === 204) return null;

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }

  return res.json();
}


// ── Goals ──────────────────────────────────────────────────

export const goals = {
  list:     ()           => request('/goals'),
  get:      (id)         => request(`/goals/${id}`),
  create:   (data)       => request('/goals', { method: 'POST', body: JSON.stringify(data) }),
  update:   (id, data)   => request(`/goals/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete:   (id)         => request(`/goals/${id}`, { method: 'DELETE' }),
  complete: (id, value)  => request(`/goals/${id}/complete`, { method: 'PATCH', body: JSON.stringify({ value }) }),
  deadline: (id, data)   => request(`/goals/${id}/deadline`, { method: 'PATCH', body: JSON.stringify(data) }),
};


// ── Tasks (nested under goals) ─────────────────────────────

export const tasks = {
  add:      (goalId, title) =>
    request(`/goals/${goalId}/tasks`, { method: 'POST', body: JSON.stringify({ title }) }),

  update:   (goalId, taskId, title) =>
    request(`/goals/${goalId}/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify({ title }) }),

  delete:   (goalId, taskId) =>
    request(`/goals/${goalId}/tasks/${taskId}`, { method: 'DELETE' }),

  complete: (goalId, taskId, value) =>
    request(`/goals/${goalId}/tasks/${taskId}/complete`, { method: 'PATCH', body: JSON.stringify({ value }) }),

  move:     (goalId, taskId, direction) =>
    request(`/goals/${goalId}/tasks/${taskId}/move`, { method: 'PATCH', body: JSON.stringify({ direction }) }),
};


// ── Subtasks (nested under tasks) ──────────────────────────

export const subtasks = {
  add:      (goalId, taskId, title) =>
    request(`/goals/${goalId}/tasks/${taskId}/subtasks`, { method: 'POST', body: JSON.stringify({ title }) }),

  update:   (goalId, taskId, subtaskId, title) =>
    request(`/goals/${goalId}/tasks/${taskId}/subtasks/${subtaskId}`, { method: 'PUT', body: JSON.stringify({ title }) }),

  delete:   (goalId, taskId, subtaskId) =>
    request(`/goals/${goalId}/tasks/${taskId}/subtasks/${subtaskId}`, { method: 'DELETE' }),

  complete: (goalId, taskId, subtaskId, value) =>
    request(`/goals/${goalId}/tasks/${taskId}/subtasks/${subtaskId}/complete`, { method: 'PATCH', body: JSON.stringify({ value }) }),

  move:     (goalId, taskId, subtaskId, direction) =>
    request(`/goals/${goalId}/tasks/${taskId}/subtasks/${subtaskId}/move`, { method: 'PATCH', body: JSON.stringify({ direction }) }),
};


// ── Task List (priority queue) ─────────────────────────────

export const taskList = {
  list:           ()           => request('/task-list'),
  create:         (data)       => request('/task-list', { method: 'POST', body: JSON.stringify(data) }),
  update:         (id, data)   => request(`/task-list/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete:         (id)         => request(`/task-list/${id}`, { method: 'DELETE' }),
  complete:       (id)         => request(`/task-list/${id}/complete`, { method: 'PATCH' }),
  reorder:        (id, pos)    => request(`/task-list/reorder?item_id=${id}`, { method: 'PATCH', body: JSON.stringify({ new_position: pos }) }),
  listCompleted:  ()           => request('/task-list/completed'),
  clearCompleted: ()           => request('/task-list/completed', { method: 'DELETE' }),
};


// ── Analytics ──────────────────────────────────────────────

export const analytics = {
  goals:    () => request('/analytics/goals'),
  taskList: () => request('/analytics/task-list'),
};


// ── Tags ───────────────────────────────────────────────────

export const tags = {
  list:   ()    => request('/tags'),
  add:    (tag) => request('/tags', { method: 'POST', body: JSON.stringify({ tag }) }),
  delete: (tag) => request(`/tags/${encodeURIComponent(tag)}`, { method: 'DELETE' }),
};
