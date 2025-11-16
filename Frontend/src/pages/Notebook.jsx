import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/notebook.css";

export default function Notebook() {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadError, setUploadError] = useState("");

  const navigate = useNavigate();

  async function loadNotes() {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8080/api/notes/all", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Failed to fetch notes");

      const data = await res.json();
      const loadedNotes = Array.isArray(data) ? data : [];
      setNotes(loadedNotes);
      if (loadedNotes.length > 0) {
        setSelectedNote(loadedNotes[0]);
      }
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

  // ------------------------------
  // Upload File as Note Handler
  // ------------------------------
  async function handleUploadNote() {
    setUploadError("");

    if (!uploadFile || uploadFile.type !== "text/plain") {
      setUploadError("Please upload a valid .txt file.");
      return;
    }

    try {
      const text = await uploadFile.text();
      const token = localStorage.getItem("token");

      const res = await fetch("http://localhost:8080/api/notes/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: uploadTitle || "Uploaded Note",
          note_text: text,
        }),
      });

      if (!res.ok) {
        const errBody = await res.text();
        console.error("Upload failed:", res.status, errBody);
        setUploadError("Upload failed: " + errBody);
        return;
      }

      setShowUploadModal(false);
      setUploadTitle("");
      setUploadFile(null);
      await loadNotes(); // refresh notes
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError("Something went wrong during upload.");
    }
  }

  return (
    <div className="container-fluid py-4">
      <div className="row g-4">
        {/* LEFT SIDEBAR */}
        <div className="col-4">
          <div className="d-flex gap-3 mb-4">
            <button
              className="btn btn-secondary w-50"
              onClick={() => setShowUploadModal(true)}
            >
              Upload
            </button>
            <button
              className="btn btn-primary w-50"
              onClick={() => navigate("/notes")}
            >
              New
            </button>
          </div>

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
                <div
                  key={note.id}
                  className={`card p-3 notebook-note-card ${
                    selectedNote?.id === note.id ? "bg-light border-primary" : ""
                  }`}
                  onClick={() => setSelectedNote(note)}
                  style={{ cursor: "pointer" }}
                >
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
          <div className="card p-4 h-100 d-flex flex-column">
            {!selectedNote ? (
              <div className="editor-placeholder text-muted">No note selected.</div>
            ) : (
              <>
                <h5 className="mb-3">{selectedNote.title || "(Untitled)"}</h5>
                <div
                  style={{
                    whiteSpace: "pre-wrap",
                    flexGrow: 1,
                    overflowY: "auto",
                  }}
                >
                  {selectedNote.note_text || "(No content)"}
                </div>
                <button
                  className="btn btn-outline-primary mt-4 align-self-end"
                  onClick={() => navigate("/notes", { state: selectedNote })}
                >
                  Update this note
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* -------------------------
          Upload Modal Overlay
      -------------------------- */}
      {showUploadModal && (
        <div className="modal show d-block" tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Upload Note from File</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowUploadModal(false)}
                />
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label className="form-label">Note Title</label>
                  <input
                    type="text"
                    className="form-control"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    placeholder="Enter title"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Upload .txt File</label>
                  <input
                    type="file"
                    accept=".txt"
                    className="form-control"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                  />
                </div>
                {uploadError && (
                  <div className="alert alert-danger">{uploadError}</div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  className="btn btn-secondary"
                  onClick={() => setShowUploadModal(false)}
                >
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={handleUploadNote}>
                  Upload Note
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
