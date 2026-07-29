"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AdminTokenMeta,
  ApiRequestError,
  connectDomain,
  createAdminToken,
  listAdminTokens,
  listSecrets,
  logout,
  registerDomain,
  revokeAdminToken,
  rotateAdminToken,
  upsertSecret,
} from "@/lib/api";
import {
  clearSession,
  getAccessToken,
  getDomainAdminToken,
  getRefreshToken,
  getSelectedTokenId,
  getServiceId,
  setDomainAdminToken,
  setSelectedTokenId,
  setServiceId,
} from "@/lib/session";

function prefixOf(token: AdminTokenMeta): string {
  return token.token_prefix || token.prefix || `#${token.id}`;
}

export default function DashboardPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [tokens, setTokens] = useState<AdminTokenMeta[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [rawToken, setRawToken] = useState<string>("");
  const [cartridgeType, setCartridgeType] = useState("courier");
  const [serviceId, setServiceIdState] = useState<string>("");
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
  const [connectResult, setConnectResult] = useState<string | null>(null);

  const selected = useMemo(
    () => tokens.find((t) => t.id === selectedId) || null,
    [tokens, selectedId],
  );

  const refreshTokens = useCallback(async (token: string) => {
    const res = await listAdminTokens(token);
    const active = res.tokens.filter((t) => !t.revoked_at);
    setTokens(active);
    setSelectedId((current) => {
      const preferred = getSelectedTokenId();
      const next =
        active.find((t) => t.id === preferred)?.id ??
        active.find((t) => t.id === current)?.id ??
        active[0]?.id ??
        null;
      if (next != null) setSelectedTokenId(next);
      else setSelectedTokenId(null);
      return next;
    });
  }, []);

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
    refreshTokens(token).catch((err) => {
      setError(err instanceof Error ? err.message : "Не удалось загрузить токены");
    });
    if (sid && admin) {
      refreshSecretKeys(sid, admin).catch(() => {
        /* token may be stale */
      });
    }
  }, [router, refreshTokens, refreshSecretKeys]);

  function fail(err: unknown) {
    const message =
      err instanceof ApiRequestError
        ? err.message
        : err instanceof Error
          ? err.message
          : "Ошибка запроса";
    setError(message);
  }

  async function onLogout() {
    try {
      const refresh = getRefreshToken();
      if (refresh) await logout(refresh);
    } catch {
      /* ignore */
    }
    clearSession();
    setServiceId(null);
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
      setSelectedId(created.id);
      setSelectedTokenId(created.id);
      setInfo("Токен создан. Сохраните значение — повторно его не покажем.");
      await refreshTokens(accessToken);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRevoke() {
    if (!accessToken || selectedId == null) return;
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      await revokeAdminToken(accessToken, selectedId);
      if (rawToken) setDomainAdminToken(null);
      setRawToken("");
      setSelectedId(null);
      setSelectedTokenId(null);
      setInfo(`Токен #${selectedId} отозван.`);
      await refreshTokens(accessToken);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRotate() {
    if (!accessToken || selectedId == null) return;
    setBusy(true);
    setError(null);
    setInfo(null);
    try {
      const created = await rotateAdminToken(accessToken, selectedId, {
        name: selected?.name || "console",
      });
      setRawToken(created.token);
      setDomainAdminToken(created.token);
      setSelectedId(created.id);
      setSelectedTokenId(created.id);
      setInfo("Токен ротирован. Новое значение сохранено локально.");
      await refreshTokens(accessToken);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRegisterDomain(e: FormEvent) {
    e.preventDefault();
    if (!rawToken.trim()) {
      setError("Сначала создайте DOMAIN_ADMIN_TOKEN (кнопка «Создать токен»).");
      return;
    }
    setBusy(true);
    setError(null);
    setInfo(null);
    setConnectResult(null);
    try {
      const res = await registerDomain(rawToken.trim(), {
        cartridge_type: cartridgeType.trim() || "courier",
      });
      setServiceIdState(res.service_id);
      setServiceId(res.service_id);
      setInfo(`Домен зарегистрирован: ${res.service_id} (${res.status})`);
      await refreshSecretKeys(res.service_id, rawToken.trim());
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
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  function clearBoundService() {
    setServiceIdState("");
    setServiceId(null);
    setSecretKeys([]);
    setConnectResult(null);
    setAttachOpen(false);
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
    setConnectResult(null);
    try {
      const res = await connectDomain(serviceId.trim(), rawToken.trim());
      setConnectResult(JSON.stringify(res, null, 2));
      setInfo(`Домен ${serviceId} подключён.`);
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
          <button type="button" className="btn btn-ghost" onClick={onLogout}>
            Выйти
          </button>
        </header>

        <section className="section">
          <h2>Tenant Account</h2>
          <p>Токен домена и регистрация картриджа</p>

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
            <button
              type="button"
              className="btn btn-ghost"
              disabled={busy || !accessToken}
              onClick={() =>
                accessToken &&
                refreshTokens(accessToken).catch(fail)
              }
            >
              Обновить список
            </button>
          </div>

          {tokens.length > 0 ? (
            <div className="token-list" role="listbox" aria-label="Admin tokens">
              {tokens.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  role="option"
                  aria-selected={t.id === selectedId}
                  data-active={t.id === selectedId}
                  onClick={() => {
                    setSelectedId(t.id);
                    setSelectedTokenId(t.id);
                  }}
                >
                  <strong>
                    #{t.id}
                    {t.name ? ` · ${t.name}` : ""}
                  </strong>
                  <span className="meta">
                    {prefixOf(t)}
                    {t.created_at ? ` · ${t.created_at}` : ""}
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <p style={{ marginBottom: "1.25rem", color: "var(--ink-soft)" }}>
              Активных токенов пока нет — создайте первый.
            </p>
          )}

          <div className="token-row">
            <div className={`token-box${rawToken ? "" : " empty"}`}>
              {rawToken ||
                "Здесь появится raw DOMAIN_ADMIN_TOKEN после create / rotate"}
            </div>
            <div className="token-actions">
              <button
                type="button"
                className="btn btn-danger"
                disabled={busy || selectedId == null}
                onClick={onRevoke}
              >
                Revoke
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={busy || selectedId == null}
                onClick={onRotate}
              >
                Rotate
              </button>
            </div>
          </div>

          <form className="domain-block" onSubmit={onRegisterDomain}>
            <div className="field">
              <label htmlFor="cartridge">Тип картриджа</label>
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
              disabled={busy || Boolean(serviceId)}
            >
              Зарегистрировать домен
            </button>
          </form>

          {!serviceId ? (
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
          ) : (
            <div className="service-chip" role="status">
              <div>
                <span className="service-chip-label">Домен</span>
                <code className="service-chip-id">{serviceId}</code>
              </div>
              <button
                type="button"
                className="linkish"
                onClick={clearBoundService}
              >
                Сбросить
              </button>
            </div>
          )}

          {serviceId ? (
            <div className="setup-block">
              <h2>Подключение домена</h2>
              <p className="lede">Заполните secrets и подключите картридж</p>

              {secretKeys.length > 0 ? (
                <p className="secret-keys">
                  Уже заданы ключи:{" "}
                  {secretKeys.map((k) => (
                    <code key={k}>{k} </code>
                  ))}
                </p>
              ) : null}

              <form onSubmit={onSaveSecrets}>
                <div className="hint">
                  В целях безопасности создайте в вашей Domain DB отдельных
                  пользователей, которые могут читать/писать только FSM-таблицы{" "}
                  <code>fsm_states</code>, <code>fsm_transitions</code>,{" "}
                  <code>fsm_graph_meta</code>, <code>fsm_actions</code> (не
                  business-таблицы). Host и имя БД те же, в URL — user/password
                  graph-учёток. Шаблон:{" "}
                  <code>database/sql/domain/002_platform_graph_db_users.sql</code>
                </div>

                <div className="field">
                  <label htmlFor="graph-read">graph_database_url (read)</label>
                  <p className="hint-inline">
                    Подсказка: пользователь вроде <code>fsm_graph_ro</code> —
                    SELECT на graph-таблицы
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
                    Подсказка: пользователь вроде <code>fsm_graph_rw</code> —
                    SELECT/INSERT/UPDATE на graph-таблицы
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
                  <p className="hint-inline">
                    URL вашего domain service (courier), например{" "}
                    <code>http://127.0.0.1:8100</code>
                  </p>
                  <input
                    id="contract-url"
                    value={contractBaseUrl}
                    onChange={(e) => setContractBaseUrl(e.target.value)}
                    placeholder="http://127.0.0.1:8100"
                    required
                  />
                </div>

                <div className="field">
                  <label htmlFor="contract-secret">contract_shared_secret</label>
                  <p className="hint-inline">
                    Тот же секрет, что <code>CONTRACT_SHARED_SECRET</code> в{" "}
                    <code>.env</code> домена
                  </p>
                  <input
                    id="contract-secret"
                    type="password"
                    autoComplete="off"
                    value={contractSecret}
                    onChange={(e) => setContractSecret(e.target.value)}
                    placeholder="тот же, что в domains/courier/.env"
                  />
                </div>

                <div className="toolbar" style={{ marginTop: "0.5rem" }}>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ width: "auto", minWidth: "12rem" }}
                    disabled={busy}
                  >
                    Сохранить secrets
                  </button>
                  <button
                    type="button"
                    className="btn btn-accent"
                    style={{ minWidth: "12rem" }}
                    disabled={busy}
                    onClick={onConnect}
                  >
                    Подключить домен
                  </button>
                </div>
              </form>

              {connectResult ? (
                <div className="probe-panel" style={{ marginTop: "1rem" }}>
                  <pre>{connectResult}</pre>
                </div>
              ) : null}
            </div>
          ) : null}

          {error ? <div className="msg msg-error">{error}</div> : null}
          {info ? <div className="msg msg-ok">{info}</div> : null}
        </section>
      </div>
    </main>
  );
}
