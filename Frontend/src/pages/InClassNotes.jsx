import { useState, useMemo } from "react";
import "../styles/notes.css";

export default function InClassNotes() {
  const [text, setText] = useState("");

  // ----- LIVE STATS -----
  const stats = useMemo(() => {
    const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
    const chars = text.length;
    const readingMin = Math.max(1, Math.ceil(words / 200));   // avg reading speed
    const speakingSec = Math.ceil(words / 2.5);                // avg speaking speed

    return { words, chars, readingMin, speakingSec };
  }, [text]);

  // ----- SAVE ACTION -----
  async function handleSave() {
    if (!text.trim()) return;

    try {
      await fetch("http://127.0.0.1:8080/api/notes/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: text })
      });

      console.log("Saved to notebook");
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="ic-page container-fluid">
      <div className="row h-100">

        <div className="col-12 d-flex flex-column position-relative">

          {/* HEADER BAR */}
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="mb-0">In-Class Notes</h2>

            <button
              className="btn ic-save-btn"
              onClick={handleSave}
            >
              Save to Notebook
            </button>
          </div>

          {/* MAIN TEXTAREA */}
          <textarea
            className="form-control flex-grow-1 ic-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Start typing..."
          />

          {/* QUESTIONS OVERLAY (existing) */}
          <div className="ic-questions-overlay">
            <h5 className="ic-q-title">Questions</h5>
            <div className="ic-q-scroll"></div>
          </div>

          {/* NEW STATS OVERLAY — bottom-left */}
          <div className="ic-stats-overlay">
            <h5 className="ic-stats-title">Stats</h5>

            <div className="ic-stats-item">Words: {stats.words}</div>
            <div className="ic-stats-item">Characters: {stats.chars}</div>
            <div className="ic-stats-item">Reading time: {stats.readingMin} min</div>
            <div className="ic-stats-item">Speaking time: {stats.speakingSec}s</div>
          </div>

        </div>
      </div>
    </div>
  );
}
