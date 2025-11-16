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
  // ---------------------------
  // Live Stats (Enhanced)
  // ---------------------------
  // ---------------------------
  // Live Stats (Minimal Version)
  // ---------------------------
  const stats = useMemo(() => {
    const trimmed = text.trim();

    // Words
    const words = trimmed ? trimmed.split(/\s+/).filter(Boolean).length : 0;

    // Characters
    const chars = text.length;

    // Sentences
    const sentencesArr = trimmed ? trimmed.split(/[.!?]+/).filter(Boolean) : [];
    const sentences = sentencesArr.length;

    // Average words per sentence
    const avgWordsPerSentence =
      sentences > 0 ? Math.round(words / sentences) : 0;

    // Unique words
    const cleanedWords = trimmed
      .toLowerCase()
      .replace(/[^\w\s]/g, "")
      .split(/\s+/)
      .filter(Boolean);

    const uniqueWords = new Set(cleanedWords).size;

    // Top 5 letters
    const letters = text
      .toLowerCase()
      .replace(/[^a-z]/g, "")
      .split("");

    const freq = {};
    letters.forEach((l) => {
      freq[l] = (freq[l] || 0) + 1;
    });

    const topLetters = Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([char, count]) => `${char}: ${count}`);

    return {
      words,
      chars,
      uniqueWords,
      topLetters,
      avgWordsPerSentence,
    };
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
      const res = await fetch(
        "http://localhost:5000/api/ai/generate-questions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ text: trimmed }),
        }
      );

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

                <div className="ic-stats-overlay">
          <h5 className="ic-stats-title">Stats</h5>

          <div className="ic-stats-item">Words: {stats.words}</div>
          <div className="ic-stats-item">Characters: {stats.chars}</div>
          <div className="ic-stats-item">Unique words: {stats.uniqueWords}</div>

          <div className="ic-stats-item">
            Top letters:{" "}
            {stats.topLetters.length > 0
              ? stats.topLetters.join(", ")
              : "—"}
          </div>

          <div className="ic-stats-item">
            Avg words/sentence: {stats.avgWordsPerSentence}
          </div>
        </div>

      </div>
    </div>
  );
}
