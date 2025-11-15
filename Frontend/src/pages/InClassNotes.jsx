import { useState, useEffect } from "react";
import "../styles/notes.css";

export default function InClassNotes() {
  const [text, setText] = useState("");

  const words = text.trim().length === 0 ? 0 : text.trim().split(/\s+/).length;
  const chars = text.length;
  const readingTime = (words / 180).toFixed(2);
  const speakingTime = (words / 130).toFixed(2);

  useEffect(() => {
    function handleKeydown(e) {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      const ctrlOrCmd = isMac ? e.metaKey : e.ctrlKey;

      if (ctrlOrCmd && e.shiftKey && e.key.toLowerCase() === "y") {
        e.preventDefault();
        console.log("Running typo check...");
      }
    }

    document.addEventListener("keydown", handleKeydown);
    return () => document.removeEventListener("keydown", handleKeydown);
  }, []);

  return (
    <div className="container-fluid py-4">

      <div className="row g-4">

        {/* LEFT SIDE - 75% */}
        <div className="col-12 col-xl-9">

          <textarea
            className="form-control mb-3"
            placeholder="Classroom input..."
            rows={14}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="card p-3 mb-3">
            <div><strong>Words:</strong> {words}</div>
            <div><strong>Characters:</strong> {chars}</div>
            <div><strong>Reading time:</strong> {readingTime} min</div>
            <div><strong>Speaking time:</strong> {speakingTime} min</div>
          </div>

          <button className="btn btn-primary w-100">
            Export to .txt
          </button>

          <p className="text-muted small mt-3 mb-0">
            Shortcut: <strong>Ctrl + Shift + Y</strong> to check typos
          </p>

        </div>

        {/* RIGHT SIDE - 25% */}
        <div className="col-12 col-xl-3 d-flex flex-column">

          <h3 className="mb-3">Questions</h3>

          <div className="card p-3 mb-4 flex-grow-0" style={{ maxHeight: "250px", overflowY: "auto" }}>
            <div className="questions-list"></div>
          </div>

          <div className="card p-3 flex-grow-1" style={{ overflowY: "auto" }}>
            <div className="ai-output"></div>
          </div>

        </div>

      </div>

    </div>
  );
}
