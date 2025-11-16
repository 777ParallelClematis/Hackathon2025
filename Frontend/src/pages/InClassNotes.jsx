import { useState, useMemo } from "react";
import "../styles/notes.css";

export default function InClassNotes() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [questions, setQuestions] = useState([]);
  const [loadingQ, setLoadingQ] = useState(false);
  const [savedMsg, setSavedMsg] = useState("");

  // ---------------------------
  // Live Stats
  // ---------------------------
  const stats = useMemo(() => {
    const trimmed = text.trim();
    const words = trimmed ? trimmed.split(/\s+/).length : 0;
    const chars = text.length;
    const readingMin = Math.max(1, Math.ceil(words / 200));
    const speakingSec = Math.ceil(words / 2.5);

    return { words, chars, readingMin, speakingSec };
  }, [text]);

  // Retrieve stored access token
  function getToken() {
    return localStorage.getItem("token");
  }

  // ---------------------------
  // Save Notes to DB
  // ---------------------------
  async function handleSave() {
    const trimmedText = text.trim();
    const trimmedTitle = title.trim();
    if (!trimmedText) return;

    const token = getToken();
    if (!token) {
      console.error("No auth token found; cannot save note");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/notes/save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          note_text: trimmedText,
          title: trimmedTitle || "Untitled Note",
        }),
      });

      if (!res.ok) {
        const errBody = await res.text();
        console.error("Save failed:", res.status, errBody);
        return;
      }

      // SUCCESS → Clear fields + show message
      setText("");
      setTitle("");
      setSavedMsg("Note saved!");

      setTimeout(() => setSavedMsg(""), 2500);
    } catch (err) {
      console.error("Save error:", err);
    }
  }

  // ---------------------------
  // Delete a single question
  // ---------------------------
  function removeQuestion(index) {
    setQuestions((prev) => prev.filter((_, i) => i !== index));
  }

  // ---------------------------
  // Generate Questions (via backend)
  // ---------------------------
  async function generateQuestions() {
    const trimmed = text.trim();
    if (!trimmed) return;

    const token = getToken();
    if (!token) {
      console.error("No auth token found; cannot call AI");
      return;
    }

    setLoadingQ(true);
    setQuestions([]);

    try {
      const res = await fetch("http://localhost:5000/api/ai/generate-questions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: trimmed }),
      });

      if (!res.ok) {
        const errBody = await res.text();
        console.error(
          "AI endpoint failed:",
          res.status,
          res.statusText,
          errBody
        );
        setLoadingQ(false);
        return;
      }

      const data = await res.json();

      if (Array.isArray(data.questions)) {
        setQuestions(data.questions);
      } else {
        console.error("Unexpected AI response format:", data);
      }
    } catch (err) {
      console.error("AI Request Failed:", err);
    } finally {
      setLoadingQ(false);
    }
  }

  // ---------------------------
  // Render
  // ---------------------------
  return (
    <div className="ic-page">
      <div className="ic-wrapper position-relative">
        
        {/* Header Bar */}
        <div className="ic-header">
          <h2>In-Class Notes</h2>

          <div className="ic-header-buttons">
            <button className="btn ic-save-btn" onClick={handleSave}>
              Save to Notebook
            </button>

            <button
              className="btn ic-generate-btn"
              onClick={generateQuestions}
              disabled={loadingQ}
            >
              {loadingQ ? "Generating..." : "Generate Questions"}
            </button>
          </div>
        </div>

        {/* Title Input */}
        <input
          className="ic-title-input"
          type="text"
          placeholder="Enter note title..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        {/* Main Typing Area */}
        <textarea
          className="ic-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Start typing..."
        />

        {/* Save Notification */}
        {savedMsg && <div className="ic-save-notification">{savedMsg}</div>}

        {/* Questions Overlay */}
        <div className="ic-questions-overlay">
          <h5 className="ic-q-title">Questions</h5>

          <div className="ic-q-bubbles">
            {!loadingQ && questions.length === 0 && (
              <div className="ic-q-empty">No questions yet</div>
            )}

            {loadingQ && <div className="ic-q-empty">Working...</div>}

            {questions.map((q, i) => (
              <div key={i} className="ic-q-bubble">
                <span className="ic-q-text">{q}</span>
                <button
                  className="ic-q-close"
                  onClick={() => removeQuestion(i)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Overlay */}
        <div className="ic-stats-overlay">
          <h5 className="ic-stats-title">Stats</h5>
          <div className="ic-stats-item">Words: {stats.words}</div>
          <div className="ic-stats-item">Characters: {stats.chars}</div>
          <div className="ic-stats-item">
            Reading time: {stats.readingMin} min
          </div>
          <div className="ic-stats-item">
            Speaking time: {stats.speakingSec}s
          </div>
        </div>
      </div>
    </div>
  );
}
