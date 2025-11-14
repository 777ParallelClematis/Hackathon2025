import "../styles/notes.css";

export default function InClassNotes() {
  return (
    <div className="notes-container">

      <div className="notes-left">
        
        <div className="notes-controls">
          <div className="toggle-group">
            <label>Formatting</label>
            <button>OFF/ON</button>
          </div>

          <div className="toggle-group">
            <label>Typos</label>
            <button>OFF/ON</button>
          </div>
        </div>

        <textarea
          className="notes-input"
          placeholder="Classroom input..."
        ></textarea>

        <button className="export-button">Export to .txt</button>
      </div>

      <div className="notes-right">
        <h3 className="section-title">Questions</h3>

        <div className="questions-list">
          {/* API-generated questions go here */}
        </div>

        <div className="ai-output">
          {/* Gemini-generated explanation */}
        </div>
      </div>

    </div>
  );
}
