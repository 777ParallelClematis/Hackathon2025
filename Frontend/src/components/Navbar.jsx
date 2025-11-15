import { NavLink, useNavigate } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    console.log("Logging out...");
    navigate("/");
  }

  return (
    <nav className="nb-nav">

      {/* LEFT — App Name */}
      <div className="nb-brand">ManuMatic</div>

      {/* CENTER MENU */}
      <div className="nb-center">
        <NavLink 
          to="/notes"
          className={({ isActive }) => isActive ? "nb-item active" : "nb-item"}
        >
          Notes
        </NavLink>

        <NavLink 
          to="/learn"
          className={({ isActive }) => isActive ? "nb-item active" : "nb-item"}
        >
          Revision
        </NavLink>

        <NavLink 
          to="/notebook"
          className={({ isActive }) => isActive ? "nb-item active" : "nb-item"}
        >
          Notebook
        </NavLink>
      </div>

      {/* RIGHT — Logout */}
      <button className="nb-logout" onClick={handleLogout}>
        Logout
      </button>

    </nav>
  );
}
