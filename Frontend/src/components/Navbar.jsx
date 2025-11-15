import { Link, useNavigate } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    console.log("Logging out...");
    navigate("/");
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark px-4">

      {/* Logo / Brand */}
      <Link className="navbar-brand fw-bold" to="/notes">
        NoteBuddy
      </Link>

      {/* Mobile toggle */}
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      {/* Collapsible area */}
      <div className="collapse navbar-collapse" id="navbarContent">

        {/* Left Links */}
        <ul className="navbar-nav me-auto">
          <li className="nav-item">
            <Link className="nav-link" to="/notes">Notes</Link>
          </li>

          <li className="nav-item">
            <Link className="nav-link" to="/learn">Revision</Link>
          </li>

          <li className="nav-item">
            <Link className="nav-link" to="/notebook">Notebook</Link>
          </li>
        </ul>

        {/* Right - Logout */}
        <button className="btn btn-outline-light" onClick={handleLogout}>
          Logout
        </button>

      </div>

    </nav>
  );
}
