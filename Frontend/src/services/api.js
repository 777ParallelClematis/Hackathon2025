// Frontend/src/services/api.js

// Base URL (no trailing slash recommended, e.g. "http://127.0.0.1:8080")
const RAW_API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8080";

// Normalize to avoid double slashes
const API_BASE_URL = RAW_API_BASE_URL.endsWith("/")
  ? RAW_API_BASE_URL.slice(0, -1)
  : RAW_API_BASE_URL;

// ---------- helpers ----------

// Decode a JWT and return the payload object
function decodeJwtPayload(token) {
  try {
    const [, payload] = token.split(".");
    const json = atob(payload);
    const decoded = JSON.parse(json);
    console.log("Decoded JWT payload:", decoded);
    return decoded;
  } catch (err) {
    console.error("Failed to decode JWT:", err);
    return null;
  }
}

// Extract user id from JWT payload (adjust if needed once you see the payload)
function extractUserIdFromPayload(payload) {
  if (!payload) return null;

  // Try the common claim names – tweak this once you see your payload.
  return (
    payload.user_id ||  // e.g. {"user_id": "69187eac3c..."}
    payload.sub ||      // often used for "subject"
    payload.id ||       // sometimes just "id"
    null
  );
}

async function postJSON(path, body, extraHeaders = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.message || "Request failed");
  }
  return data;
}

// Simple GET helper (useful for /notes etc.)
export async function getJSON(path, extraHeaders = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders,
    },
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.message || "Request failed");
  }
  return data;
}

// ------------- exported helpers your components can use -------------

// These now auto-pull student_id from localStorage if not passed in
export function analyzeAnswer({ title, student_id, student_response }) {
  const sid =
    student_id || localStorage.getItem("student_id") || "TEMP-STUDENT-ID";

  return postJSON("/analyze", {
    title,
    student_id: sid,
    student_response,
  });
}

export function classifyAnswer({ title, student_id, student_response }) {
  const sid =
    student_id || localStorage.getItem("student_id") || "TEMP-STUDENT-ID";

  return postJSON("/classify", {
    title,
    student_id: sid,
    student_response,
  });
}

/**
 * Login:
 *  - POSTs to /api/users/login
 *  - saves token in localStorage as "token"
 *  - decodes token to extract user id and saves it as "student_id"
 *  - returns the response data so Login.jsx can still call useAuth.login(data.token)
 */
export async function login(email, password) {
    // Corrected: Pass email and password as an object to postJSON
    const data = await postJSON("/api/users/login", { email, password });
  
    if (data.token) {
      // store token
      localStorage.setItem("token", data.token);
  
      // decode and store student_id
      const payload = decodeJwtPayload(data.token);
      const userId = extractUserIdFromPayload(payload);
  
      if (userId) {
        localStorage.setItem("student_id", userId);
        console.log("Saved student_id:", userId);
      } else {
        console.warn("Could not extract user id from JWT payload.");
      }
    }
  
    return data;
  }

// If your register endpoint also returns a token, this will behave like login
export async function registerUser({ name, email, password }) {
  const data = await postJSON("/api/users/register", { name, email, password });

  if (data.token) {
    localStorage.setItem("token", data.token);

    const payload = decodeJwtPayload(data.token);
    const userId = extractUserIdFromPayload(payload);

    if (userId) {
      localStorage.setItem("student_id", userId);
      console.log("Saved student_id (from register):", userId);
    }
  }

  return data;
}

// Handy helper if you want elsewhere
export function getStudentId() {
  return localStorage.getItem("student_id");
}
