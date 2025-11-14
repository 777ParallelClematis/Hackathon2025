import "../styles/notebook.css";

export default function Notebook() {
  return (
    <div className="container-fluid py-4">

      <div className="row g-4">

        {/* LEFT SIDEBAR */}
        <div className="col-4">

          {/* Buttons Row */}
          <div className="d-flex gap-3 mb-4">
            <button className="btn btn-secondary w-50">Upload</button>
            <button className="btn btn-primary w-50">New</button>
          </div>

          {/* File List */}
          <div className="d-flex flex-column gap-3">

            <div className="card p-4"></div>
            <div className="card p-4"></div>
            <div className="card p-4"></div>

            <div className="card p-4 text-center text-muted">
              File name, Timestamp, content
            </div>

            <div className="card p-4"></div>

          </div>
        </div>

        {/* RIGHT EDITOR PANEL */}
        <div className="col-8">
          <div className="card p-4 h-100">
            {/* Editor placeholder */}
            <div className="editor-placeholder text-muted">
              Your editor UI will go here.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
