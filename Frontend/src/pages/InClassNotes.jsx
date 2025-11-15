import "../styles/notes.css"; // overrides only

export default function InClassNotes() {
  return (
    <div className="container-fluid py-4">

      <div className="row g-4">

        {/* LEFT PANEL */}
        <div className="col-12 col-lg-4">

          <div className="card p-3 mb-4">
            <h5 className="mb-3">Controls</h5>

            <div className="d-flex justify-content-between align-items-center mb-3">
              <label className="fw-medium">Formatting</label>
              <button className="btn btn-sm btn-outline-secondary">OFF/ON</button>
            </div>

            <div className="d-flex justify-content-between align-items-center">
              <label className="fw-medium">Typos</label>
              <button className="btn btn-sm btn-outline-secondary">OFF/ON</button>
            </div>
          </div>

          <textarea
            className="form-control mb-3"
            placeholder="Classroom input..."
            rows={12}
          />

          <button className="btn btn-primary w-100">
            Export to .txt
          </button>

        </div>

        {/* RIGHT PANEL */}
        <div className="col-12 col-lg-8 d-flex flex-column">

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
