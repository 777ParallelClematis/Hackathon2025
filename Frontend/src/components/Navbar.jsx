import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import "../styles/navbar.css";


export default function Navbar() {
  const { logout } = useAuth();

  function toggleTheme() {
    document.body.classList.toggle("light");
  }

  return (
   <nav className="nb-nav">
  
  {/* LEFT BRAND */}
  <div className="nb-left">
    <div className="nb-brand">Manumatic</div>
  </div>

  {/* CENTER NAV ITEMS */}
<div className="nb-center">
  <NavLink to="/notes" className="nb-item">In Class</NavLink>
  <NavLink to="/learn" className="nb-item">Revision</NavLink>
  <NavLink to="/notebook" className="nb-item">Notes</NavLink>
</div>



  {/* RIGHT SIDE (toggle + logout) */}
  <div className="nb-right">
    <button
      className="nb-toggle"
      onClick={() => document.body.classList.toggle("light")}
      aria-label="Toggle theme"
    >
      🌓
    </button>

    <button className="nb-logout" onClick={logout}>
      Logout
    </button>
  </div>

</nav>

  );
}
