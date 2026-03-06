const DEFAULT_API_URL = "http://127.0.0.1:8000";
export const API_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL;

export class ApiError extends Error {
  constructor(status, message, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function toQueryString(params) {
  const searchParams = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    searchParams.set(key, String(value));
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : "";
}

export async function apiFetch(path, options = {}) {
  const url = `${API_URL}${path}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  let res;
  try {
    res = await fetch(url, { ...options, headers });
  } catch {
    throw new Error(`تعذر الوصول إلى الخادم على ${API_URL}. تأكد من تشغيل الـAPI وإعدادات CORS.`);
  }
  if (res.status === 204) return null;

  const text = await res.text();
  const data = text ? safeJsonParse(text) : null;

  if (!res.ok) {
    const message = (data && data.detail) || res.statusText || "فشل الطلب";
    throw new ApiError(res.status, message, data);
  }

  return data;
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export function getUsers() {
  return apiFetch("/users");
}

export function createUser(payload) {
  return apiFetch("/users", { method: "POST", body: JSON.stringify(payload) });
}

export function getUser(userId) {
  return apiFetch(`/users/${userId}`);
}

export function updateUser(userId, payload) {
  return apiFetch(`/users/${userId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export function deleteUser(userId) {
  return apiFetch(`/users/${userId}`, { method: "DELETE" });
}

export function getProjects() {
  return apiFetch("/projects");
}

export function createProject(payload) {
  return apiFetch("/projects", { method: "POST", body: JSON.stringify(payload) });
}

export function getProject(projectId) {
  return apiFetch(`/projects/${projectId}`);
}

export function updateProject(projectId, payload) {
  return apiFetch(`/projects/${projectId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export function deleteProject(projectId) {
  return apiFetch(`/projects/${projectId}`, { method: "DELETE" });
}

export function getTasks(params) {
  return apiFetch(`/tasks${toQueryString(params)}`);
}

export function createTask(payload) {
  return apiFetch("/tasks", { method: "POST", body: JSON.stringify(payload) });
}
