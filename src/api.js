
const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000/api"
).replace(/\/+$/, "");

export async function api(path, options = {}) {
  const token = localStorage.getItem("bluewater_token");
  const headers = new Headers(options.headers || {});

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  const body =
    response.status === 204
      ? null
      : await response.json().catch(() => null);

  if (!response.ok) {
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : detail;

    throw new Error(message || `Request failed (${response.status})`);
  }

  return body;
}

export const apiBaseUrl = API_URL;
