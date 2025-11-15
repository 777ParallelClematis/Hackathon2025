import { useEffect, useState } from "react";
import "../styles/notebook.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8080";

// helper for GET requests
async function getJSON(path) {
  const res = await fetch(`${API_URL}${path}`);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.message || "Request failed");
  }
  return data;
}

export default function Notebook() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState("");

  // student id (same pattern as Revision.jsx)
  const [studentId] = useState(
    () => localStorage.getItem("student_id") || "TEMP-STUDENT-ID"
  );

  async function loadNotes() {
    try {
      setLoading(true);
      setError("");

      // hit the same backend route used by Revision.jsx
      const data = await getJSON(`/notes?student_id=${encodeURIComponent(studentId)}`);

      // backend returns { notes: [...] }
      const list = data.notes || [];
      setNotes(list);
    } catch (err) {
      console.error("Error loading notes:", err);
      setError(err.message || "Could not load your notes.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNotes();
  }, [studentId]);

  return (
    <div className="container-fluid py-4">
      <div className="row g-4">

        {/* LEFT SIDEBAR */}
        <div className="col-4">

          {/* Buttons Row */}
          <div className="d-flex gap-3 mb-4">
            <button className="btn btn-secondary w-50">Upload</button>
            <button className="btn btn-primary w-50">New</button>
          </div>

          {/* Error message */}
          {error && (
            <div className="alert alert-danger mb-3">
              {error}
            </div>
          )}

          {/* Notes List */}
          <div
            className="d-flex flex-column gap-3"
            style={{ overflowY: "auto", maxHeight: "80vh" }}
          >
            {loading && (
              <div className="card p-4 text-muted text-center">Loading...</div>
            )}

            {!loading && notes.length === 0 && !error && (
              <div className="card p-4 text-muted text-center">
                No notes saved yet.
              </div>
            )}

            {!loading && notes.map((note) => (
              <div key={note._id} className="card p-3 notebook-note-card">

                <div className="small text-muted mb-1">
                  {note.created_at
                    ? new Date(note.created_at).toLocaleString()
                    : "No date"}
                </div>

                <div className="fw-bold mb-1">
                  {note.title || "Untitled note"}
                </div>

                <div className="notebook-note-preview">
                  {note.note_text
                    ? (note.note_text.length > 120
                        ? note.note_text.slice(0, 120) + "…"
                        : note.note_text)
                    : <span className="text-muted">No content</span>}
                </div>

              </div>
            ))}
          </div>
        </div>

        {/* RIGHT EDITOR PANEL */}
        <div className="col-8">
          <div className="card p-4 h-100">
            <div className="editor-placeholder text-muted">
              Your editor UI will go here.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
