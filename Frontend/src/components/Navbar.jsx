import { Link, useNavigate } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    console.log("Logging out...");
    navigate("/");
  }

  return (
    <nav className="nb-nav">

      {/* Center menu */}
      <div className="nb-center">
        <Link className="nb-item" to="/notes">Notes</Link>
        <Link className="nb-item" to="/learn">Revision</Link>
        <Link className="nb-item" to="/notebook">Notebook</Link>
      </div>

      {/* Logout button */}
      <button className="nb-logout" onClick={handleLogout}>
        Logout
      </button>

    </nav>
  );
}
