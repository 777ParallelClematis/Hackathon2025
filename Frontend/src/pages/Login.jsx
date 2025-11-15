import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import "../styles/login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      const res = await fetch("https://hackathon2025-jqk7.onrender.com/api/users/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        alert("Invalid credentials.");
        return;
      }

      const data = await res.json();
      login(data.token);

      navigate("/notes");
    } catch (err) {
      console.error("Login error:", err);
      alert("Login failed.");
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
            <Link to="/register" className="text-primary">Create one</Link>
          </p>
        </form>

      </div>
    </div>
  );
}
