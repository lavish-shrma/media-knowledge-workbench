import { useState } from "react";

export default function AuthPanel({ onLogin, onRegister, onLogout, email }) {
  const [formEmail, setFormEmail] = useState(email || "");
  const [password, setPassword] = useState("");

  return (
    <section className="panel">
      <h2>Authentication</h2>
      <div className="auth-form">
        <input
          type="email"
          placeholder="Email"
          value={formEmail}
          onChange={(event) => setFormEmail(event.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <div className="auth-actions">
          <button type="button" onClick={() => onRegister(formEmail, password)}>
            Register
          </button>
          <button type="button" onClick={() => onLogin(formEmail, password)}>
            Login
          </button>
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </section>
  );
}
