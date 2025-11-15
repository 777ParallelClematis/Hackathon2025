const API_BASE_URL = import.meta.env.VITE_API_URL; // Vite-style

async function postJSON(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.message || "Request failed");
  }
  return data;
}

// exported helpers your components can use
export function analyzeAnswer({ title, student_id, student_response }) {
  return postJSON("/analyze", { title, student_id, student_response });
}

export function classifyAnswer({ title, student_id, student_response }) {
  return postJSON("/classify", { title, student_id, student_response });
}

export function login({ email, password }) {
  return postJSON("/api/users/login", { email, password });
}

export function registerUser({ name, email, password }) {
  return postJSON("/api/users/register", { name, email, password });
}
