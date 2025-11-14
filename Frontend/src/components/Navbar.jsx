import { Link, useNavigate } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    // clear tokens later when JWT is added
    console.log("Logging out...");
    navigate("/");
  }

  return (
    <nav className="nb-nav">
      <div className="nb-left">
        <span className="nb-logo">NoteBuddy</span>
      </div>

      <div className="nb-links">
        <Link to="/notes" className="nb-link">Notes</Link>
        <Link to="/learn" className="nb-link">Revision</Link>
      </div>

      <button className="nb-logout" onClick={handleLogout}>
        Logout
      </button>
    </nav>
  );
}
