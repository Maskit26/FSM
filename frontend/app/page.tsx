"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login, register, verifyEmail, ApiRequestError } from "@/lib/api";
import { getAccessToken, postLoginPath, setSession } from "@/lib/session";

type Mode = "login" | "register";

export default function LandingPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("reauth") === "1") {
        setMode("login");
        setInfo("Сессия истекла — войдите снова.");
      }
    }
  }, []);

  useEffect(() => {
    if (getAccessToken()) {
      router.replace(postLoginPath());
    }
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      if (mode === "register") {
        const reg = await register(email.trim(), password);
        if (reg.verification_token) {
          await verifyEmail(reg.verification_token);
          setInfo("Аккаунт создан и подтверждён. Выполняем вход…");
          const session = await login(email.trim(), password);
          setSession(session.access_token, session.refresh_token);
          router.push(postLoginPath());
          return;
        }
        setInfo(
          "Регистрация принята. Подтвердите email, затем войдите (вкладка «Вход»).",
        );
        setMode("login");
        return;
      }

      const session = await login(email.trim(), password);
      setSession(session.access_token, session.refresh_token);
      router.push(postLoginPath());
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Ошибка запроса";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <div className="hero">
        <section className="hero-visual" aria-label="FSM Platform">
          <h1 className="brand">
            FSM
            <br />
            Platform
          </h1>
          <p className="brand-sub">
            Регистрация арендатора и управление доменом: токены и регистрация
            домена.
          </p>
        </section>

        <section className="hero-panel">
          <div className="auth-shell">
            <div className="tabs" role="tablist">
              <button
                type="button"
                className="tab"
                role="tab"
                aria-selected={mode === "register"}
                onClick={() => {
                  setMode("register");
                  setError(null);
                  setInfo(null);
                }}
              >
                Регистрация
              </button>
              <button
                type="button"
                className="tab"
                role="tab"
                aria-selected={mode === "login"}
                onClick={() => {
                  setMode("login");
                  setError(null);
                  setInfo(null);
                }}
              >
                Вход
              </button>
            </div>

            <form onSubmit={onSubmit}>
              <div className="field">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="password">
                  Пароль
                  {mode === "register" ? " (от 12 символов, буквы и цифры)" : ""}
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete={
                    mode === "login" ? "current-password" : "new-password"
                  }
                  required
                  minLength={mode === "register" ? 12 : 1}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy
                  ? "…"
                  : mode === "register"
                    ? "Зарегистрироваться"
                    : "Войти"}
              </button>
            </form>

            {error ? <div className="msg msg-error">{error}</div> : null}
            {info ? <div className="msg msg-ok">{info}</div> : null}
          </div>
        </section>
      </div>
    </main>
  );
}
