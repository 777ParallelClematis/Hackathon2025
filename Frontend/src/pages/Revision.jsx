import "../styles/revision.css"; // overrides only

export default function Revision() {
  return (
    <div className="container-fluid py-4">

      {/* Import Row */}
      <div className="row mb-4 align-items-center">

        <div className="col-auto">
          <button className="btn btn-primary">Import .txt</button>
        </div>

        <div className="col-auto">
          <input 
            type="file"
            accept=".txt"
            className="form-control"
          />
        </div>

      </div>

      {/* Main Content */}
      <div className="row g-4">

        {/* Notes Review */}
        <div className="col-12 col-lg-8">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">Notes</h5>
            <div className="notes-review"></div>
          </div>
        </div>

        {/* Feedback */}
        <div className="col-12 col-lg-4">
          <div className="card p-4 h-100" style={{ overflowY: "auto" }}>
            <h5 className="mb-3">AI Feedback</h5>
            <div className="feedback-panel"></div>
          </div>
        </div>

      </div>

      {/* Cheat Sheet */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="card p-4">
            <h5 className="mb-3">Cheat Sheet</h5>
            <div className="cheatsheet-box"></div>
          </div>
        </div>
      </div>

    </div>
  );
}
