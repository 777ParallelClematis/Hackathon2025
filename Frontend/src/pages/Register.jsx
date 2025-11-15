import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import "../styles/login.css"; // reuse styling

export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:5000/api/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const msg = await res.text();
        setError("Registration failed: " + msg);
        return;
      }

      const data = await res.json();

      // immediately authenticate the user
      login(data.token);

      navigate("/notes");
    } catch (err) {
      console.error(err);
      setError("Registration error.");
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">

        <div className="login-left">
          <h1 className="login-title">Create Account</h1>
          <p className="login-subtitle">
            Fast & easy note-taking anywhere.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          
          {error && <p className="text-danger">{error}</p>}

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
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm" className="form-label">Confirm Password</label>
            <input
              id="confirm"
              type="password"
              className="login-input"
              placeholder="Confirm your password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="login-button">
            Create Account
          </button>

          <p className="mt-3 text-center">
            Already have an account?{" "}
            <Link to="/" className="text-primary">Login</Link>
          </p>

        </form>

      </div>
    </div>
  );
}
