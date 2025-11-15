import { useState } from "react";
import "../styles/revision.css"; // keep for overrides only

const API_URL = import.meta.env.VITE_API_URL || "https://hackathon2025-jqk7.onrender.com/";

// Small helper to call backend
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

export default function Revision() {
  // 1) Notes from uploaded file (just for display)
  const [notesText, setNotesText] = useState("");

  // 2) Student response typed by user
  const [studentResponse, setStudentResponse] = useState("");

  // 3) Title + student id (title must match backend reference)
  const [title, setTitle] = useState("Lady bugs"); // default example
  const [studentId, setStudentId] = useState(
    () => localStorage.getItem("student_id") || "TEMP-STUDENT-ID"
  );

  // 4) Results from backend
  const [classifyResult, setClassifyResult] = useState(null);
  const [analyzeResult, setAnalyzeResult] = useState(null);

  // 5) UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // --- handlers ---

  // Upload notes file (.txt) → store text locally and show it
  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setNotesText(event.target.result || "");
    };
    reader.readAsText(file);
  }

  // Shared validation before hitting backend
  function validateBeforeSend() {
    if (!title.trim()) {
      setError("Please enter a title for these notes (it should match the backend reference).");
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

    try {
      const payload = {
        title,
        student_id: studentId,
        student_response: studentResponse,
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

    try {
      const payload = {
        title,
        student_id: studentId,
        student_response: studentResponse,
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
      {/* Top Row: Upload + Controls */}
      <div className="row mb-4 align-items-center">
        {/* Upload notes */}
        <div className="col-auto">
          <label className="form-label mb-0">
            <strong>1. Upload your notes (.txt)</strong>
          </label>
          <input
            type="file"
            accept=".txt"
            className="form-control"
            onChange={handleFileUpload}
          />
        </div>

        {/* Title input */}
        <div className="col-auto">
          <label className="form-label mb-0">
            <strong>Notes title</strong>
          </label>
          <input
            type="text"
            className="form-control"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Lady bugs"
          />
        </div>

        {/* Action buttons */}
        <div className="col-auto d-flex gap-2 align-items-end">
          <button
            className="btn btn-outline-secondary"
            onClick={handleClassify}
            disabled={loading}
          >
            {loading ? "Working..." : "Classify"}
          </button>
          <button
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Working..." : "Analyze"}
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

      {/* Main Content */}
      <div className="row g-4">
        {/* Notes Review Panel */}
        <div className="col-6">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">Notes (from uploaded file)</h5>
            <div className="notes-review">
              {notesText ? (
                <pre style={{ whiteSpace: "pre-wrap" }}>{notesText}</pre>
              ) : (
                <p className="text-muted">Upload a .txt file to see your notes here.</p>
              )}
            </div>
          </div>
        </div>

        {/* Student Response Panel */}
        <div className="col-6">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">2. Your Response</h5>
            <textarea
              className="form-control"
              rows={10}
              placeholder="Write your answer here based on the notes..."
              value={studentResponse}
              onChange={(e) => setStudentResponse(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Feedback + Cheat Sheet */}
      <div className="row mt-4 g-4">
        {/* AI Feedback */}
        <div className="col-6">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">AI Feedback</h5>

            {classifyResult && (
              <div className="mb-3">
                <h6>Classification (/classify)</h6>
                <p>
                  <strong>{classifyResult.classification}</strong> (score{" "}
                  {classifyResult.score})
                </p>
                <p>{classifyResult.feedback}</p>
              </div>
            )}

            {analyzeResult && (
              <div>
                <h6>Analysis (/analyze)</h6>
                <p>
                  <strong>{analyzeResult.classification}</strong> (score{" "}
                  {analyzeResult.score})
                </p>
                <p>{analyzeResult.feedback}</p>

                {analyzeResult.keywords && analyzeResult.keywords.length > 0 && (
                  <>
                    <h6 className="mt-3 mb-1">Keywords</h6>
                    <ul className="mb-0">
                      {analyzeResult.keywords.map((kw, i) => (
                        <li key={i}>{kw}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}

            {!classifyResult && !analyzeResult && (
              <p className="text-muted">
                After you write your response, click <strong>Classify</strong> or{" "}
                <strong>Analyze</strong> to see feedback here.
              </p>
            )}
          </div>
        </div>

        {/* Cheat Sheet */}
        <div className="col-6">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">Cheat Sheet</h5>
            <div className="cheatsheet-box">
              {analyzeResult && analyzeResult.cheat_sheet ? (
                <pre style={{ whiteSpace: "pre-wrap" }}>
                  {analyzeResult.cheat_sheet}
                </pre>
              ) : (
                <p className="text-muted">
                  Once <strong>/analyze</strong> is implemented to return a cheat_sheet, it
                  will show up here.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
