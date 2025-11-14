import { useState } from "react";
import "../styles/login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    console.log("Logging in...", { email, password });
  }

  return (
    <div className="login-container">
  <div className="login-card">
    
    <div className="login-left">
      <h1 className="login-title">NoteBuddy</h1>
      <p className="login-subtitle">
        Learn better on campus<br/>and off campus
      </p>
    </div>

    <form className="login-form">
      <input className="login-input" />
      <input className="login-input" />
      <button className="login-button">Login</button>
    </form>

  </div>
</div>
  );
}
