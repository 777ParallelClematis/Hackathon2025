import { useEffect, useState } from "react";
import "../styles/notebook.css";

export default function Notebook() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadNotes() {
    try {
      const token = localStorage.getItem("token"); // from login system

      const res = await fetch("http://localhost:5000/api/notes/all", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch notes");
      }

      const data = await res.json();
      setNotes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading notes:", err);
      setNotes([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNotes();
  }, []);

  return (
    <div className="container-fluid py-4">
      <div className="row g-4">
        {/* LEFT SIDEBAR */}
        <div className="col-4">
          {/* Buttons */}
          <div className="d-flex gap-3 mb-4">
            <button className="btn btn-secondary w-50">Upload</button>
            <button className="btn btn-primary w-50">New</button>
          </div>

          {/* Notes List */}
          <div
            className="d-flex flex-column gap-3"
            style={{ overflowY: "auto", maxHeight: "80vh" }}
          >
            {loading && (
              <div className="card p-4 text-muted text-center">Loading...</div>
            )}

            {!loading && notes.length === 0 && (
              <div className="card p-4 text-muted text-center">
                No notes saved yet.
              </div>
            )}

            {!loading &&
              notes.map((note) => (
                <div key={note.id} className="card p-3 notebook-note-card">
                  <div className="small text-muted mb-2">
                    {new Date(note.created_at).toLocaleString()}
                  </div>

                  <div className="fw-bold mb-1">{note.title || "(Untitled)"}</div>

                  <div className="notebook-note-preview">
                    {(note.note_text || "").length > 120
                      ? note.note_text.slice(0, 120) + "…"
                      : note.note_text}
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* RIGHT PANEL */}
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
