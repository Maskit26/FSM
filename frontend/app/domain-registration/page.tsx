"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ApiRequestError,
  connectDomain,
  createAdminToken,
  isSessionExpiredError,
  listSecrets,
  logout,
  registerDomain,
  upsertSecret,
} from "@/lib/api";
import {
  clearAuthSession,
  clearSession,
  getAccessToken,
  getDomainAdminToken,
  getRefreshToken,
  getServiceId,
  isDomainConnected,
  setDomainAdminToken,
  setDomainConnected,
  setServiceId,
} from "@/lib/session";

export default function DomainRegistrationPage() {
  const router = useRouter();
  const connectRef = useRef<HTMLElement | null>(null);
  const [ready, setReady] = useState(false);
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [rawToken, setRawToken] = useState("");
  const [cartridgeType, setCartridgeType] = useState("courier");
  const [serviceId, setServiceIdState] = useState("");
  const [attachOpen, setAttachOpen] = useState(false);
  const [attachDraft, setAttachDraft] = useState("");
  const [secretKeys, setSecretKeys] = useState<string[]>([]);
  const [graphReadUrl, setGraphReadUrl] = useState("");
  const [graphWriteUrl, setGraphWriteUrl] = useState("");
  const [contractBaseUrl, setContractBaseUrl] = useState("http://127.0.0.1:8100");
  const [contractSecret, setContractSecret] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [scrollToConnect, setScrollToConnect] = useState(0);

  const refreshSecretKeys = useCallback(
    async (sid: string, adminToken: string) => {
      const res = await listSecrets(sid, adminToken);
      setSecretKeys(res.keys || []);
    },
    [],
  );

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/");
      return;
    }
    setAccessTokenState(token);
    const admin = getDomainAdminToken() || "";
    setRawToken(admin);
    const sid = getServiceId() || "";
    setServiceIdState(sid);
    setReady(true);
    if (sid && admin) {
      refreshSecretKeys(sid, admin).catch(() => {});
    }
  }, [router, refreshSecretKeys]);

  useEffect(() => {
    if (!scrollToConnect) return;
    const el = connectRef.current;
    if (!el) return;
    const t = window.setTimeout(() => {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
    return () => window.clearTimeout(t);
  }, [scrollToConnect]);

  function redirectToLogin() {
    clearAuthSession();
    router.replace("/?reauth=1");
  }

  function fail(err: unknown) {
    if (isSessionExpiredError(err)) {
      redirectToLogin();
      return;
    }
    setError(
      err instanceof ApiRequestError
        ? err.message
        : err instanceof Error
          ? err.message
          : "Ошибка запроса",
    );
  }

  async function onLogout() {
    try {
      const refresh = getRefreshToken();
      if (refresh) await logout(refresh);
    } catch {
      /* ignore */
    }
    clearSession();
    router.replace("/");
  }

  async function onCreateToken() {
    if (!accessToken) return;
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const created = await createAdminToken(accessToken, { name: "console" });
      setRawToken(created.token);
      setDomainAdminToken(created.token);
      setInfo("Токен создан. Сохраните значение — повторно его не покажем.");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRegisterDomain(e: FormEvent) {
    e.preventDefault();
    if (!rawToken.trim()) {
      setError("Сначала создайте DOMAIN_ADMIN_TOKEN.");
      return;
    }
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const res = await registerDomain(rawToken.trim(), {
        cartridge_type: cartridgeType.trim() || "courier",
      });
      setServiceIdState(res.service_id);
      setServiceId(res.service_id);
      setInfo(`Домен зарегистрирован: ${res.service_id}`);
      await refreshSecretKeys(res.service_id, rawToken.trim());
      setScrollToConnect((n) => n + 1);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onAttachExisting(e: FormEvent) {
    e.preventDefault();
    const sid = attachDraft.trim();
    if (!sid) {
      setError("Укажите service_id.");
      return;
    }
    if (!rawToken.trim()) {
      setError("Сначала нужен DOMAIN_ADMIN_TOKEN.");
      return;
    }
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      setServiceIdState(sid);
      setServiceId(sid);
      setAttachOpen(false);
      setAttachDraft("");
      await refreshSecretKeys(sid, rawToken.trim());
      setInfo(`Привязан домен ${sid}`);
      setScrollToConnect((n) => n + 1);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onSaveSecrets(e: FormEvent) {
    e.preventDefault();
    if (!rawToken.trim() || !serviceId.trim()) {
      setError("Нужны DOMAIN_ADMIN_TOKEN и service_id.");
      return;
    }
    const pairs: [string, string][] = [
      ["graph_database_url", graphReadUrl.trim()],
      ["graph_write_database_url", graphWriteUrl.trim()],
      ["contract_base_url", contractBaseUrl.trim()],
      ["contract_shared_secret", contractSecret.trim()],
    ];
    const missing = pairs.filter(([, v]) => !v);
    if (missing.length) {
      setError(`Заполните поля: ${missing.map(([k]) => k).join(", ")}`);
      return;
    }
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      for (const [key, value] of pairs) {
        await upsertSecret(serviceId.trim(), rawToken.trim(), key, value);
      }
      await refreshSecretKeys(serviceId.trim(), rawToken.trim());
      setInfo("Secrets сохранены. Можно подключать домен.");
      setGraphReadUrl("");
      setGraphWriteUrl("");
      setContractSecret("");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onConnect() {
    if (!rawToken.trim() || !serviceId.trim()) {
      setError("Нужны DOMAIN_ADMIN_TOKEN и service_id.");
      return;
    }
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      await connectDomain(serviceId.trim(), rawToken.trim());
      setDomainConnected(true);
      router.push("/dashboard");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  if (!ready) {
    return (
      <main className="page">
        <div className="dash">Загрузка…</div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="dash">
        <header className="dash-top">
          <h1 className="dash-brand">FSM Platform</h1>
          <div className="toolbar" style={{ marginBottom: 0 }}>
            {isDomainConnected() ? (
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => router.push("/dashboard")}
              >
                ← Dashboard
              </button>
            ) : null}
            <button type="button" className="btn btn-ghost" onClick={onLogout}>
              Выйти
            </button>
          </div>
        </header>

        <section className="section">
          <h2>Токен и регистрация домена</h2>
          <p>Создайте DOMAIN_ADMIN_TOKEN, затем зарегистрируйте домен</p>

          <div className="toolbar">
            <button
              type="button"
              className="btn btn-primary"
              style={{ width: "auto", minWidth: "10rem" }}
              disabled={busy}
              onClick={onCreateToken}
            >
              Создать токен
            </button>
          </div>

          <div className={`token-box${rawToken ? "" : " empty"}`} style={{ marginBottom: "1.25rem" }}>
            {rawToken || "Здесь появится raw DOMAIN_ADMIN_TOKEN после создания"}
          </div>

          <form className="domain-block" onSubmit={onRegisterDomain}>
            <div className="field">
              <label htmlFor="cartridge">Тип домена</label>
              <input
                id="cartridge"
                value={cartridgeType}
                onChange={(e) => setCartridgeType(e.target.value)}
                placeholder="courier"
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-accent"
              style={{ minWidth: "14rem" }}
              disabled={busy || !rawToken}
            >
              Зарегистрировать домен
            </button>
          </form>

          <div className="attach-wrap">
            {!attachOpen ? (
              <button
                type="button"
                className="linkish"
                onClick={() => setAttachOpen(true)}
              >
                Уже есть service_id?
              </button>
            ) : (
              <form className="attach-form" onSubmit={onAttachExisting}>
                <input
                  value={attachDraft}
                  onChange={(e) => setAttachDraft(e.target.value)}
                  placeholder="svc_courier_…"
                  aria-label="Существующий service_id"
                  autoFocus
                />
                <button type="submit" className="btn btn-ghost" disabled={busy}>
                  Привязать
                </button>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => {
                    setAttachOpen(false);
                    setAttachDraft("");
                  }}
                >
                  Отмена
                </button>
              </form>
            )}
          </div>
        </section>

        <section
          className="section setup-block"
          ref={connectRef}
          id="connect-setup"
        >
          <h2>Подключение домена</h2>
          <p className="lede">
            {serviceId ? (
              <>
                Secrets и connect для <code>{serviceId}</code>
              </>
            ) : (
              "Сначала зарегистрируйте или привяжите service_id выше"
            )}
          </p>

          {secretKeys.length > 0 ? (
            <p className="secret-keys">
              Уже заданы ключи:{" "}
              {secretKeys.map((k) => (
                <code key={k}>{k} </code>
              ))}
            </p>
          ) : null}

          <form onSubmit={onSaveSecrets}>
            <fieldset disabled={!serviceId || busy} className="connect-fieldset">
              <div className="hint">
                В целях безопасности создайте в Domain DB пользователей только
                на FSM-таблицы <code>fsm_states</code>,{" "}
                <code>fsm_transitions</code>, <code>fsm_graph_meta</code>,{" "}
                <code>fsm_actions</code>. Host/БД те же — в URL user/password
                graph-учёток (<code>fsm_graph_ro</code> /{" "}
                <code>fsm_graph_rw</code>).
              </div>

              <div className="field">
                <label htmlFor="graph-read">graph_database_url (read)</label>
                <p className="hint-inline">
                  Пользователь вроде <code>fsm_graph_ro</code>
                </p>
                <input
                  id="graph-read"
                  type="password"
                  autoComplete="off"
                  value={graphReadUrl}
                  onChange={(e) => setGraphReadUrl(e.target.value)}
                  placeholder="mysql+mysqlconnector://fsm_graph_ro:…@host:3306/db"
                />
              </div>

              <div className="field">
                <label htmlFor="graph-write">graph_write_database_url (write)</label>
                <p className="hint-inline">
                  Пользователь вроде <code>fsm_graph_rw</code>
                </p>
                <input
                  id="graph-write"
                  type="password"
                  autoComplete="off"
                  value={graphWriteUrl}
                  onChange={(e) => setGraphWriteUrl(e.target.value)}
                  placeholder="mysql+mysqlconnector://fsm_graph_rw:…@host:3306/db"
                />
              </div>

              <div className="field">
                <label htmlFor="contract-url">contract_base_url</label>
                <p className="hint-inline">URL domain service (courier)</p>
                <input
                  id="contract-url"
                  value={contractBaseUrl}
                  onChange={(e) => setContractBaseUrl(e.target.value)}
                  required={Boolean(serviceId)}
                />
              </div>

              <div className="field">
                <label htmlFor="contract-secret">contract_shared_secret</label>
                <p className="hint-inline">
                  = <code>CONTRACT_SHARED_SECRET</code> в .env домена
                </p>
                <input
                  id="contract-secret"
                  type="password"
                  autoComplete="off"
                  value={contractSecret}
                  onChange={(e) => setContractSecret(e.target.value)}
                />
              </div>

              <div className="toolbar" style={{ marginTop: "0.5rem" }}>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ width: "auto", minWidth: "12rem" }}
                  disabled={!serviceId || busy}
                >
                  Сохранить secrets
                </button>
                <button
                  type="button"
                  className="btn btn-accent"
                  style={{ minWidth: "12rem" }}
                  disabled={!serviceId || busy}
                  onClick={onConnect}
                >
                  Подключить домен
                </button>
              </div>
            </fieldset>
          </form>
        </section>

        {error ? <div className="msg msg-error">{error}</div> : null}
        {info ? <div className="msg msg-ok">{info}</div> : null}
      </div>
    </main>
  );
}
