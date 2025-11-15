import { useState } from "react";
import "../styles/notes.css";

export default function InClassNotes() {
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    if (!text.trim()) return;

    setSaving(true);

    try {
      // TODO: replace with your actual backend route
      const response = await fetch("http://localhost:5000/api/notes/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ content: text })
      });

      if (!response.ok) {
        throw new Error("Failed to save note");
      }

      console.log("Note saved successfully");
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="ic-page container-fluid">

      <div className="row h-100">

        {/* FULL WIDTH — NOTES + OVERLAY */}
        <div className="col-12 d-flex flex-column position-relative">

          {/* HEADER BAR */}
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="mb-0">In-Class Notes</h2>

            <button
              className="btn btn-primary ic-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save"}
            </button>
          </div>

          {/* TEXT INPUT */}
          <textarea
            className="form-control flex-grow-1 ic-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Start typing..."
          />

          {/* QUESTIONS OVERLAY */}
          <div className="ic-questions-overlay">
            <h5 className="ic-q-title">Questions</h5>
            <div className="ic-q-scroll">
              {/* questions go here */}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
