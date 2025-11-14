import "../styles/revision.css";

export default function Revision() {
  return (
    <div className="revision-container">

      <div className="upload-row">
        <button className="import-button">Import .txt</button>
        <input type="file" accept=".txt" className="file-input" />
      </div>

      <div className="revision-content">

        <div className="notes-review">
          {/* text showing uploaded notes */}
        </div>

        <div className="feedback-panel">
          {/* Gemini feedback + tips */}
        </div>

      </div>

      <div className="cheatsheet-box">
        {/* mini cheat sheet */}
      </div>

    </div>
  );
}
