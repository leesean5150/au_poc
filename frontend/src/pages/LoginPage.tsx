import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/client";
import { ApiError } from "../api/http";
import { setToken } from "../lib/auth";
import { Card } from "../components/primitives";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { access_token } = await login(email, password);
      setToken(access_token);
      navigate("/admin");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? "Invalid email or password"
          : "Something went wrong — please try again",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div style={{ width: 360, maxWidth: "90vw" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div className="brand">Guest CRM</div>
        </div>
        <Card title="Sign in">
          <form onSubmit={onSubmit}>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <span className="muted" style={{ fontSize: 13 }}>
                  Email
                </span>
                <input
                  className="input"
                  type="email"
                  required
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="demo.admin@poc.local"
                />
              </label>
              <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <span className="muted" style={{ fontSize: 13 }}>
                  Password
                </span>
                <input
                  className="input"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </label>
              {error && (
                <div style={{ color: "var(--danger, #c0392b)", fontSize: 13 }}>
                  {error}
                </div>
              )}
              <button className="btn" type="submit" disabled={submitting}>
                {submitting ? "Signing in…" : "Sign in"}
              </button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
