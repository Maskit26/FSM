"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AdminTokenMeta,
  ApiRequestError,
  ScheduleRow,
  WebhookRow,
  createAdminToken,
  createSchedule,
  createWebhook,
  connectDomain,
  deactivateWebhook,
  deleteSecret,
  fetchCatalog,
  graphPublish,
  inboundHookUrl,
  isSessionExpiredError,
  listAdminTokens,
  listSchedules,
  listSecrets,
  listWebhooks,
  logout,
  pauseSchedule,
  reloadDomain,
  resumeSchedule,
  revokeAdminToken,
  rotateAdminToken,
  telegramLink,
  telegramWebhookUrl,
  upsertSecret,
  workerRestart,
  workerStatus,
  workerStop,
} from "@/lib/api";
import {
  clearAuthSession,
  clearSession,
  getAccessToken,
  getDomainAdminToken,
  getRefreshToken,
  getServiceId,
  isDomainConnected,
  isEnvBannerDismissed,
  setDomainAdminToken,
  setEnvBannerDismissed,
  setSelectedTokenId,
} from "@/lib/session";

type TileId =
  | "token"
  | "worker"
  | "domain"
  | "input"
  | "output"
  | "secret"
  | "schedule"
  | null;


function prefixOf(token: AdminTokenMeta): string {
  return token.token_prefix || token.prefix || `#${token.id}`;
}

export default function CabinetPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [adminToken, setAdminToken] = useState("");
  const [serviceId, setServiceIdState] = useState("");
  const [openTile, setOpenTile] = useState<TileId>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [showEnvBanner, setShowEnvBanner] = useState(false);

  const [tokens, setTokens] = useState<AdminTokenMeta[]>([]);
  const [rawToken, setRawToken] = useState("");
  const [selectedTokenId, setSelectedTokenIdState] = useState<number | null>(null);

  const [workerInfo, setWorkerInfo] = useState<string>("");
  const [webhooks, setWebhooks] = useState<WebhookRow[]>([]);
  const [hookUrl, setHookUrl] = useState("");
  const [hookSecret, setHookSecret] = useState("");

  const [secretKeys, setSecretKeys] = useState<string[]>([]);
  const [secretKey, setSecretKey] = useState("");
  const [secretValue, setSecretValue] = useState("");

  const [schedules, setSchedules] = useState<ScheduleRow[]>([]);
  const [schedProcess, setSchedProcess] = useState("");
  const [schedInterval, setSchedInterval] = useState("60");

  const [domainResult, setDomainResult] = useState("");
  const [hookChannels, setHookChannels] = useState<string[]>([]);
  const [telegramUserId, setTelegramUserId] = useState("");
  const [telegramLinkUrl, setTelegramLinkUrl] = useState("");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/?reauth=1");
      return;
    }
    const sid = getServiceId();
    const admin = getDomainAdminToken();
    if (!isDomainConnected() || !sid || !admin) {
      router.replace("/domain-registration");
      return;
    }
    setAccessToken(token);
    setServiceIdState(sid);
    setAdminToken(admin);
    setRawToken(admin);
    setShowEnvBanner(!isEnvBannerDismissed());
    setReady(true);
  }, [router]);

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

  function clearMsg() {
    setError(null);
    setInfo(null);
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

  function dismissEnvBanner() {
    setEnvBannerDismissed(true);
    setShowEnvBanner(false);
  }

  function toggleTile(id: TileId) {
    clearMsg();
    setOpenTile((cur) => (cur === id ? null : id));
  }

  const loadTokens = useCallback(async () => {
    if (!accessToken) return;
    const res = await listAdminTokens(accessToken);
    const active = res.tokens.filter((t) => !t.revoked_at);
    setTokens(active);
  }, [accessToken]);

  async function onCreateToken() {
    if (!accessToken) return;
    setBusy(true);
    clearMsg();
    try {
      const created = await createAdminToken(accessToken, { name: "console" });
      setRawToken(created.token);
      setDomainAdminToken(created.token);
      setAdminToken(created.token);
      setSelectedTokenIdState(created.id);
      setSelectedTokenId(created.id);
      setInfo("Токен создан.");
      await loadTokens();
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onListTokens() {
    setBusy(true);
    clearMsg();
    try {
      await loadTokens();
      setInfo(`Активных токенов: ${(await listAdminTokens(accessToken!)).tokens.filter((t) => !t.revoked_at).length}`);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRevokeToken() {
    if (!accessToken || selectedTokenId == null) return;
    setBusy(true);
    clearMsg();
    try {
      await revokeAdminToken(accessToken, selectedTokenId);
      setInfo(`Токен #${selectedTokenId} отозван.`);
      setSelectedTokenIdState(null);
      await loadTokens();
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onRotateToken() {
    if (!accessToken || selectedTokenId == null) return;
    setBusy(true);
    clearMsg();
    try {
      const created = await rotateAdminToken(accessToken, selectedTokenId, {
        name: "console",
      });
      setRawToken(created.token);
      setDomainAdminToken(created.token);
      setAdminToken(created.token);
      setSelectedTokenIdState(created.id);
      setSelectedTokenId(created.id);
      setInfo("Токен ротирован.");
      await loadTokens();
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onWorkerStatus() {
    setBusy(true);
    clearMsg();
    try {
      const res = await workerStatus(serviceId, adminToken);
      setWorkerInfo(JSON.stringify(res, null, 2));
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onWorkerRestart() {
    setBusy(true);
    clearMsg();
    try {
      const res = await workerRestart(serviceId, adminToken);
      setWorkerInfo(JSON.stringify(res, null, 2));
      setInfo("Worker restart выполнен.");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onWorkerStop() {
    setBusy(true);
    clearMsg();
    try {
      const res = await workerStop(serviceId, adminToken);
      setWorkerInfo(JSON.stringify(res, null, 2));
      setInfo("Worker остановлен.");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onListWebhooks() {
    setBusy(true);
    clearMsg();
    try {
      const res = await listWebhooks(serviceId, adminToken);
      setWebhooks(res.webhooks || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onCreateWebhook(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    clearMsg();
    try {
      await createWebhook(serviceId, adminToken, {
        url: hookUrl.trim(),
        secret: hookSecret.trim(),
      });
      setHookUrl("");
      setHookSecret("");
      setInfo("Webhook создан.");
      const res = await listWebhooks(serviceId, adminToken);
      setWebhooks(res.webhooks || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onDeactivateWebhook(id: number) {
    setBusy(true);
    clearMsg();
    try {
      await deactivateWebhook(serviceId, adminToken, id);
      setInfo(`Webhook #${id} деактивирован.`);
      const res = await listWebhooks(serviceId, adminToken);
      setWebhooks(res.webhooks || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onListSecrets() {
    setBusy(true);
    clearMsg();
    try {
      const res = await listSecrets(serviceId, adminToken);
      setSecretKeys(res.keys || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onUpsertSecret(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    clearMsg();
    try {
      await upsertSecret(serviceId, adminToken, secretKey.trim(), secretValue);
      setSecretValue("");
      setInfo(`Secret «${secretKey.trim()}» сохранён.`);
      const res = await listSecrets(serviceId, adminToken);
      setSecretKeys(res.keys || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onDeleteSecret(key: string) {
    setBusy(true);
    clearMsg();
    try {
      await deleteSecret(serviceId, adminToken, key);
      setInfo(`Secret «${key}» удалён.`);
      const res = await listSecrets(serviceId, adminToken);
      setSecretKeys(res.keys || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onListSchedules() {
    setBusy(true);
    clearMsg();
    try {
      const res = await listSchedules(serviceId, adminToken);
      setSchedules(res.schedules || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onCreateSchedule(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    clearMsg();
    try {
      await createSchedule(serviceId, adminToken, {
        process_name: schedProcess.trim(),
        interval_seconds: Number(schedInterval) || 60,
      });
      setInfo("Расписание создано.");
      const res = await listSchedules(serviceId, adminToken);
      setSchedules(res.schedules || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onPauseSchedule(id: number) {
    setBusy(true);
    clearMsg();
    try {
      await pauseSchedule(serviceId, adminToken, id);
      setInfo(`Schedule #${id} paused.`);
      const res = await listSchedules(serviceId, adminToken);
      setSchedules(res.schedules || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onResumeSchedule(id: number) {
    setBusy(true);
    clearMsg();
    try {
      await resumeSchedule(serviceId, adminToken, id);
      setInfo(`Schedule #${id} resumed.`);
      const res = await listSchedules(serviceId, adminToken);
      setSchedules(res.schedules || []);
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onDomainReload() {
    setBusy(true);
    clearMsg();
    try {
      const res = await reloadDomain(serviceId, adminToken);
      setDomainResult(JSON.stringify(res, null, 2));
      setInfo("Catalog reload выполнен (процесс domain на :8100 не перезапускается).");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onDomainConnect() {
    setBusy(true);
    clearMsg();
    try {
      const res = await connectDomain(serviceId, adminToken);
      setDomainResult(JSON.stringify(res, null, 2));
      setInfo("Connect выполнен.");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onGraphPublish() {
    if (!window.confirm("Опубликовать новую версию графа?")) return;
    setBusy(true);
    clearMsg();
    try {
      const res = await graphPublish(serviceId, adminToken);
      setDomainResult(JSON.stringify(res, null, 2));
      setInfo("Graph published.");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onOpenInput() {
    clearMsg();
    if (openTile === "input") {
      setOpenTile(null);
      return;
    }
    setOpenTile("input");
    try {
      const cat = await fetchCatalog(serviceId, adminToken);
      setHookChannels(cat.hooks || []);
    } catch (err) {
      fail(err);
    }
  }

  async function onTelegramLink(e: FormEvent) {
    e.preventDefault();
    const uid = Number(telegramUserId);
    if (!Number.isFinite(uid)) {
      setError("Укажите user_id.");
      return;
    }
    setBusy(true);
    clearMsg();
    try {
      const res = await telegramLink(serviceId, uid);
      setTelegramLinkUrl(res.url);
      setInfo("Deep-link получен.");
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
          <div>
            <h1 className="dash-brand">Личный кабинет</h1>
            <p className="cabinet-sid">
              <code>{serviceId}</code>
            </p>
          </div>
          <button type="button" className="btn btn-ghost" onClick={onLogout}>
            Выйти
          </button>
        </header>

        {showEnvBanner ? (
          <div className="hint hint-warn env-banner" role="status">
            <div className="env-banner-head">
              <strong>Настройте SERVICE_ID в .env домена</strong>
              <button type="button" className="linkish" onClick={dismissEnvBanner}>
                Закрыть
              </button>
            </div>
            <p style={{ margin: "0.5rem 0 0" }}>
              В <code>domains/&lt;domain&gt;/.env</code> пропишите и
              перезапустите domain service:
            </p>
            <pre className="env-snippet">{`SERVICE_ID=${serviceId}`}</pre>
            <p style={{ margin: "0.5rem 0 0", fontSize: "0.85rem" }}>
              Для ручного worker в platform <code>.env</code>:{" "}
              <code>WORKER_SERVICE_ID={serviceId}</code>
            </p>
          </div>
        ) : null}

        <div className="tile-grid">
          <button
            type="button"
            className="tile"
            onClick={() => router.push("/playground")}
          >
            <span className="tile-title">Operations</span>
            <span className="tile-sub">catalog · entities · events</span>
          </button>
          <button
            type="button"
            className="tile"
            onClick={() => router.push("/e2e")}
          >
            <span className="tile-title">E2E</span>
            <span className="tile-sub">YAML scenario · report download</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "secret" ? " tile-open" : ""}`}
            onClick={() => toggleTile("secret")}
          >
            <span className="tile-title">Secret</span>
            <span className="tile-sub">upsert / list / delete</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "domain" ? " tile-open" : ""}`}
            onClick={() => toggleTile("domain")}
          >
            <span className="tile-title">Domain</span>
            <span className="tile-sub">register · connect · catalog reload · graph</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "worker" ? " tile-open" : ""}`}
            onClick={() => toggleTile("worker")}
          >
            <span className="tile-title">Worker</span>
            <span className="tile-sub">status / restart / stop</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "token" ? " tile-open" : ""}`}
            onClick={() => toggleTile("token")}
          >
            <span className="tile-title">Token</span>
            <span className="tile-sub">DOMAIN_ADMIN_TOKEN</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "input" ? " tile-open" : ""}`}
            onClick={() => onOpenInput()}
          >
            <span className="tile-title">Input</span>
            <span className="tile-sub">telegram · inbound hooks</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "output" ? " tile-open" : ""}`}
            onClick={() => toggleTile("output")}
          >
            <span className="tile-title">Output</span>
            <span className="tile-sub">outbound webhooks</span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "schedule" ? " tile-open" : ""}`}
            onClick={() => toggleTile("schedule")}
          >
            <span className="tile-title">Schedules</span>
            <span className="tile-sub">create / list / pause / resume</span>
          </button>
        </div>

        {openTile === "domain" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => router.push("/domain-registration")}
              >
                Register
              </button>
              <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onDomainConnect}>
                Connect
              </button>
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onDomainReload}>
                Reload catalog
              </button>
              <button type="button" className="btn btn-danger" disabled={busy} onClick={onGraphPublish}>
                Graph publish
              </button>
            </div>
            {domainResult ? (
              <div className="probe-panel">
                <pre>{domainResult}</pre>
              </div>
            ) : null}
          </section>
        ) : null}

        {openTile === "input" ? (
          <section className="tile-panel">
            <p className="muted" style={{ marginTop: 0 }}>
              Внешние системы бьют в эти URL. Здесь — ссылки и deep-link.
            </p>
            <div className="field">
              <label>Telegram webhook URL</label>
              <div className="token-box">{telegramWebhookUrl(serviceId)}</div>
            </div>
            <form className="tile-form" onSubmit={onTelegramLink}>
              <div className="field">
                <label htmlFor="tg-uid">user_id → deep-link</label>
                <input
                  id="tg-uid"
                  value={telegramUserId}
                  onChange={(e) => setTelegramUserId(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                Get link
              </button>
            </form>
            {telegramLinkUrl ? (
              <div className="token-box" style={{ marginTop: "0.75rem" }}>
                {telegramLinkUrl}
              </div>
            ) : null}
            <h3 style={{ margin: "1.25rem 0 0.5rem", fontSize: "1rem" }}>
              Inbound hooks
            </h3>
            {hookChannels.length === 0 ? (
              <p className="muted">Каналов в catalog нет (или catalog не загружен).</p>
            ) : (
              <ul className="plain-list">
                {hookChannels.map((ch) => (
                  <li key={ch}>
                    <code>{ch}</code>
                    <span className="meta" style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
                      {inboundHookUrl(serviceId, ch)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}

        {openTile === "output" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListWebhooks}>
                List webhooks
              </button>
            </div>
            <form className="tile-form" onSubmit={onCreateWebhook}>
              <div className="field">
                <label htmlFor="hook-url">URL</label>
                <input id="hook-url" value={hookUrl} onChange={(e) => setHookUrl(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="hook-secret">Secret (HMAC)</label>
                <input
                  id="hook-secret"
                  type="password"
                  value={hookSecret}
                  onChange={(e) => setHookSecret(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                Create webhook
              </button>
            </form>
            {webhooks.length > 0 ? (
              <ul className="plain-list">
                {webhooks.map((w) => (
                  <li key={w.id}>
                    <span>
                      #{w.id} · {w.active ? "active" : "off"} · {w.url}
                    </span>
                    {w.active ? (
                      <button
                        type="button"
                        className="btn btn-danger"
                        disabled={busy}
                        onClick={() => onDeactivateWebhook(w.id)}
                      >
                        Deactivate
                      </button>
                    ) : null}
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ) : null}

        {openTile === "token" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onCreateToken}>
                Create
              </button>
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListTokens}>
                List
              </button>
              <button type="button" className="btn btn-danger" disabled={busy || selectedTokenId == null} onClick={onRevokeToken}>
                Revoke
              </button>
              <button type="button" className="btn btn-ghost" disabled={busy || selectedTokenId == null} onClick={onRotateToken}>
                Rotate
              </button>
            </div>
            <div className={`token-box${rawToken ? "" : " empty"}`}>
              {rawToken || "Raw token после create / rotate"}
            </div>
            {tokens.length > 0 ? (
              <div className="token-list" style={{ marginTop: "1rem" }}>
                {tokens.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    data-active={t.id === selectedTokenId}
                    onClick={() => setSelectedTokenIdState(t.id)}
                  >
                    <strong>
                      #{t.id}
                      {t.name ? ` · ${t.name}` : ""}
                    </strong>
                    <span className="meta">{prefixOf(t)}</span>
                  </button>
                ))}
              </div>
            ) : null}
          </section>
        ) : null}

        {openTile === "worker" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onWorkerStatus}>
                Status
              </button>
              <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onWorkerRestart}>
                Restart
              </button>
              <button type="button" className="btn btn-danger" disabled={busy} onClick={onWorkerStop}>
                Stop
              </button>
            </div>
            {workerInfo ? (
              <div className="probe-panel">
                <pre>{workerInfo}</pre>
              </div>
            ) : null}
          </section>
        ) : null}

        {openTile === "secret" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListSecrets}>
                List
              </button>
            </div>
            <form className="tile-form" onSubmit={onUpsertSecret}>
              <div className="field">
                <label htmlFor="sec-key">Key</label>
                <input id="sec-key" value={secretKey} onChange={(e) => setSecretKey(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="sec-val">Value</label>
                <input
                  id="sec-val"
                  type="password"
                  value={secretValue}
                  onChange={(e) => setSecretValue(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                Upsert
              </button>
            </form>
            {secretKeys.length > 0 ? (
              <ul className="plain-list">
                {secretKeys.map((k) => (
                  <li key={k}>
                    <code>{k}</code>
                    <button
                      type="button"
                      className="btn btn-danger"
                      disabled={busy}
                      onClick={() => onDeleteSecret(k)}
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ) : null}

        {openTile === "schedule" ? (
          <section className="tile-panel">
            <div className="toolbar">
              <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListSchedules}>
                List
              </button>
            </div>
            <form className="tile-form" onSubmit={onCreateSchedule}>
              <div className="field">
                <label htmlFor="sched-proc">process_name</label>
                <input
                  id="sched-proc"
                  value={schedProcess}
                  onChange={(e) => setSchedProcess(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="sched-int">interval_seconds</label>
                <input
                  id="sched-int"
                  type="number"
                  min={1}
                  value={schedInterval}
                  onChange={(e) => setSchedInterval(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                Create
              </button>
            </form>
            {schedules.length > 0 ? (
              <ul className="plain-list">
                {schedules.map((s) => (
                  <li key={s.id}>
                    <span>
                      #{s.id} · {s.process_name} · {s.interval_seconds}s ·{" "}
                      {s.status || "—"}
                    </span>
                    <span className="row-actions">
                      <button
                        type="button"
                        className="btn btn-ghost"
                        disabled={busy}
                        onClick={() => onPauseSchedule(s.id)}
                      >
                        Pause
                      </button>
                      <button
                        type="button"
                        className="btn btn-ghost"
                        disabled={busy}
                        onClick={() => onResumeSchedule(s.id)}
                      >
                        Resume
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ) : null}

        {error ? <div className="msg msg-error">{error}</div> : null}
        {info ? <div className="msg msg-ok">{info}</div> : null}
      </div>
    </main>
  );
}
