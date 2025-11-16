import "../styles/revision.css";
import { useState, useEffect } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8080";

// Helpers
async function postJSON(path, body) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Request failed");
  return data;
}

async function getJSON(path) {
  const res = await fetch(`${API_URL}${path}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Request failed");
  return data;
}

export default function Revision() {
  // notes list for dropdown
  const [notesList, setNotesList] = useState([]);
  const [selectedNoteId, setSelectedNoteId] = useState("");

  // text shown in Notes panel (from dropdown or upload)
  const [notesText, setNotesText] = useState("");

  // student response typed by user
  const [studentResponse, setStudentResponse] = useState("");

  // title that gets sent to backend (matches note.title in DB)
  const [title, setTitle] = useState("");

  // student id (from localStorage or temp)
  const [studentId] = useState(
    () => localStorage.getItem("student_id") || "TEMP-STUDENT-ID"
  );

  // API results
  const [classifyResult, setClassifyResult] = useState(null);
  const [analyzeResult, setAnalyzeResult] = useState(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // load notes for this student on mount
  useEffect(() => {
    async function loadNotes() {
      try {
        setError("");
        const data = await getJSON(
          `/notes?student_id=${encodeURIComponent(studentId)}`
        );
        const list = data.notes || [];
        setNotesList(list);

        // optionally select first note by default
        if (list.length > 0) {
          const first = list[0];
          setSelectedNoteId(first._id);
          setTitle(first.title);
          setNotesText(first.note_text || "");
        }
      } catch (err) {
        console.error(err);
        setError(err.message || "Could not load your notes.");
      }
    }
    loadNotes();
  }, [studentId]);

  // file upload → override notesText (not saved to DB here, just for revision)
  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setNotesText(event.target.result || "");
    };
    reader.readAsText(file);
  }

  // when dropdown selection changes
  function handleNoteChange(e) {
    const id = e.target.value;
    setSelectedNoteId(id);

    const note = notesList.find((n) => n._id === id);
    if (note) {
      setTitle(note.title);
      setNotesText(note.note_text || "");
    } else {
      setTitle("");
      setNotesText("");
    }
  }

  // validation
  function validateBeforeSend() {
    if (!title.trim() && !notesText.trim()) {
      setError("Please upload notes or select a note title.");
      return false;
    }
    if (!studentResponse.trim()) {
      setError("Please write your response before analyzing or classifying.");
      return false;
    }
    setError("");
    return true;
  }

  async function handleClassify() {
    if (!validateBeforeSend()) return;

    setLoading(true);
    setClassifyResult(null);
    setAnalyzeResult(null); // Clear other results for a single action

    try {
      const payload = {
        note_id: selectedNoteId || null,
        title,
        student_id: studentId,
        student_response: studentResponse,
        reference_text: notesText || "", // <-- text from DB or uploaded .txt
      };

      const data = await postJSON("/classify", payload);
      setClassifyResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error calling /classify");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    if (!validateBeforeSend()) return;

    setLoading(true);
    setAnalyzeResult(null);
    setClassifyResult(null); // Clear other results for a single action

    try {
      const payload = {
        note_id: selectedNoteId || null,
        title,
        student_id: studentId,
        student_response: studentResponse,
        reference_text: notesText || "", // <-- text from DB or uploaded .txt
      };

      const data = await postJSON("/analyze", payload);
      setAnalyzeResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error calling /analyze");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-fluid py-4">
      {/* Top controls */}
      <div className="row mb-4 align-items-end g-3">
        {/* File input column */}
        <div className="col-auto">
          <label className="form-label mb-0">
            <strong>Choose File</strong>
          </label>
          <input
            type="file"
            accept=".txt"
            className="form-control"
            onChange={handleFileUpload}
          />
        </div>

        {/* Notes dropdown column */}
        <div className="col-auto">
          <label className="form-label mb-0">
            <strong>Notes title</strong>
          </label>
          <select
            className="form-select"
            value={selectedNoteId}
            onChange={handleNoteChange}
          >
            <option value="">Select one of your notes…</option>
            {notesList.map((note) => (
              <option key={note._id} value={note._id}>
                {note.title}
              </option>
            ))}
          </select>
        </div>

        {/* Action buttons column (aligned right) */}
        <div className="col-auto ms-auto d-flex gap-2">
          <button
            className="btn btn-outline-secondary"
            onClick={handleClassify}
            disabled={loading}
            // Setting min-width for uniform button size
            style={{ minWidth: "100px" }}
          >
            {loading ? "Working…" : "Classify"}
          </button>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={loading}
            // Setting min-width for uniform button size
            style={{ minWidth: "100px" }}
          >
            {loading ? "Working…" : "Analyze"}
          </button>
        </div>
      </div>

      {error && (
        <div className="row mb-3">
          <div className="col-12">
            <div className="alert alert-danger mb-0">{error}</div>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="row g-4">
        {/* Notes panel */}
        <div className="col-12 col-lg-8">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">Notes</h5>
            <div className="notes-review">
              {notesText ? (
                <pre style={{ whiteSpace: "pre-wrap" }}>{notesText}</pre>
              ) : (
                <p className="text-muted">
                  Upload a .txt file or select one of your existing notes to see
                  it here.
                </p>
              )}
            </div>

            {/* Student answer box */}
            <hr />
            <h6>Your answer</h6>
            <textarea
              className="form-control"
              rows={5}
              placeholder="Write your short answer here..."
              value={studentResponse}
              onChange={(e) => setStudentResponse(e.target.value)}
            />
          </div>
        </div>

        {/* AI Feedback panel */}
        <div className="col-12 col-lg-4">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">AI Feedback</h5>

            {loading && <p>Working on your answer...</p>}

            {!loading && !classifyResult && !analyzeResult && (
              <p className="text-muted">
                No AI feedback yet. Write a response and click{" "}
                <strong>Classify</strong> or <strong>Analyze</strong>.
              </p>
            )}

            {classifyResult && (
              <div className="mb-3">
                <h6>MiniLM Classification</h6>
                <p>
                  <strong>Status:</strong> {classifyResult.classification}
                </p>
                <p>
                  <strong>Score:</strong> {classifyResult.score}
                </p>
                <p>{classifyResult.feedback}</p>
              </div>
            )}

            {analyzeResult && (
              <div>
                <h6>Gemini Analysis</h6>
                <p>
                  <strong>Status:</strong> {analyzeResult.classification}
                </p>
                <p>
                  <strong>Score:</strong> {analyzeResult.score}
                </p>
                {/* feedback from Gemini is multi-line, so keep line breaks */}
                <p style={{ whiteSpace: "pre-line" }}>
                  {analyzeResult.feedback}
                </p>

                {analyzeResult.keywords &&
                  analyzeResult.keywords.length > 0 && (
                    <>
                      <strong>Key ideas to remember:</strong>
                      <ul>
                        {analyzeResult.keywords.map((k) => (
                          <li key={k}>{k}</li>
                        ))}
                      </ul>
                    </>
                  )}
              </div>
            )}
          </div>
        </div>

        {/* Cheat Sheet */}
        <div className="col-12 col-lg-6">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">Cheat Sheet</h5>
            <div className="cheatsheet-box">
              {analyzeResult?.cheat_sheet ? (
                <pre style={{ whiteSpace: "pre-wrap" }}>
                  {analyzeResult.cheat_sheet}
                </pre>
              ) : (
                <p className="text-muted">
                  Run <strong>Analyze</strong> to generate a mini cheat sheet
                  from your notes.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}