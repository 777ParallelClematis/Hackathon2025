import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import { login as apiLogin } from "../services/api.js"; // adjust path if needed
import "../styles/global.css";
import "../styles/backgrounds.css";   // ← add this
import "../styles/login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
  
    try {
      const data = await apiLogin({ email, password });
  
      if (data.token) {
        // this still updates the React auth context
        login(data.token);
      }
  
      navigate("/notes");
    } catch (err) {
      console.error("Login error:", err);
      alert("Login failed: " + err.message);
    }
  }
  

  return (
    <div className="login-container">
      <div className="login-card">

        <div className="login-left">
          <h1 className="login-title">NoteBuddy</h1>
          <p className="login-subtitle">
            Learn better on campus
            <br />
            and off campus
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">Email</label>
            <input
              id="email"
              type="email"
              className="login-input"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              id="password"
              type="password"
              className="login-input"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="login-button">
            Login
          </button>

          <p className="mt-3 text-center">
            Don’t have an account?{" "}
            <Link to="/register">Create one</Link>
          </p>
        </form>

        <button
  type="button"
  onClick={() => document.body.classList.toggle("light")}
  style={{
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "6px 12px",
    background: "var(--accent)",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer"
  }}
>
  Toggle Theme
</button>


      </div>
    </div>
  );
}
