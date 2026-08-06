"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ApiRequestError,
  CatalogResponse,
  enqueueProcess,
  entityActions,
  entityHistory,
  entitySnapshot,
  fetchCatalog,
  instanceStatus,
  invokeOperation,
  isSessionExpiredError,
  listEvents,
} from "@/lib/api";
import {
  clearAuthSession,
  getAccessToken,
  getDomainAdminToken,
  getServiceId,
  isDomainConnected,
} from "@/lib/session";

type Mode = "operations" | "entities" | "events";
type OpsAction = "invoke" | "enqueue";

type TreeSelection =
  | { kind: "operation"; name: string; opKind: string }
  | { kind: "process"; name: string }
  | null;

function buildRequestTemplate(operation: string): string {
  return JSON.stringify(
    {
      operation,
      params: {},
      actor: {
        actor_type: "user",
        actor_id: null,
        channel: "api",
      },
    },
    null,
    2,
  );
}

function buildEnqueueTemplate(processName: string): string {
  return JSON.stringify(
    {
      process_name: processName,
      entity_type: "order",
      entity_id: 0,
      payload: {},
      mode: "async",
      actor: {
        actor_type: "user",
        actor_id: null,
        channel: "api",
      },
    },
    null,
    2,
  );
}

function pretty(data: unknown): string {
  return JSON.stringify(data, null, 2);
}

export default function PlaygroundPage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [mode, setMode] = useState<Mode>("operations");
  const [opsAction, setOpsAction] = useState<OpsAction>("invoke");
  const [serviceId, setServiceIdState] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [selection, setSelection] = useState<TreeSelection>(null);
  const [requestJson, setRequestJson] = useState(
    '// Выберите operation\n{\n  "operation": "",\n  "params": {},\n  "actor": { "actor_type": "user", "channel": "api" }\n}',
  );
  const [responseJson, setResponseJson] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [entityType, setEntityType] = useState("order");
  const [entityId, setEntityId] = useState("");
  const [instanceId, setInstanceId] = useState("");
  const [entityActorId, setEntityActorId] = useState("");
  const [entityActorType, setEntityActorType] = useState("user");
  const [entityPayload, setEntityPayload] = useState("{\n  \n}");
  const [entityParams, setEntityParams] = useState("{\n  \n}");

  const [eventsAfterId, setEventsAfterId] = useState("0");
  const [eventsLimit, setEventsLimit] = useState("50");
  const [eventsJson, setEventsJson] = useState("");

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
    setServiceIdState(sid);
    setAdminToken(admin);
    setReady(true);
    setBusy(true);
    fetchCatalog(sid, admin)
      .then((res) => setCatalog(res))
      .catch((err) => handleErr(err))
      .finally(() => setBusy(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  function redirectToLogin() {
    clearAuthSession();
    router.replace("/?reauth=1");
  }

  function handleErr(err: unknown) {
    if (isSessionExpiredError(err)) {
      redirectToLogin();
      return;
    }
    setError(err instanceof Error ? err.message : "Ошибка запроса");
  }

  function selectOperation(name: string, opKind: string) {
    setSelection({ kind: "operation", name, opKind });
    setRequestJson(buildRequestTemplate(name));
    setError(null);
  }

  function selectProcess(name: string) {
    setSelection({ kind: "process", name });
    setRequestJson(buildEnqueueTemplate(name));
    setError(null);
  }

  async function reloadCatalog() {
    setBusy(true);
    setError(null);
    try {
      setCatalog(await fetchCatalog(serviceId, adminToken));
    } catch (err) {
      handleErr(err);
    } finally {
      setBusy(false);
    }
  }

  async function onInvoke() {
    let body: {
      operation?: string;
      params?: Record<string, unknown>;
      actor?: { actor_type?: string; actor_id?: string; channel?: string };
    };
    try {
      body = JSON.parse(requestJson) as typeof body;
    } catch {
      setError("request: невалидный JSON");
      return;
    }
    if (!body.operation) {
      setError("В request нужен operation.");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await invokeOperation(serviceId, adminToken, {
        operation: body.operation,
        params: body.params || {},
        actor: body.actor,
      });
      setResponseJson(pretty(res));
    } catch (err) {
      if (isSessionExpiredError(err)) {
        redirectToLogin();
        return;
      }
      if (err instanceof ApiRequestError) {
        setResponseJson(
          pretty({ status: err.status, error: err.message, body: err.body }),
        );
        setError(err.message);
      } else {
        handleErr(err);
      }
    } finally {
      setBusy(false);
    }
  }

  async function onEnqueue() {
    let body: {
      process_name?: string;
      entity_type?: string;
      entity_id?: number;
      payload?: Record<string, unknown>;
      mode?: string;
      actor?: { actor_type?: string; actor_id?: string; channel?: string };
      idempotency_key?: string;
    };
    try {
      body = JSON.parse(requestJson) as typeof body;
    } catch {
      setError("request: невалидный JSON");
      return;
    }
    if (!body.process_name || !body.entity_type || body.entity_id == null) {
      setError("Нужны process_name, entity_type, entity_id.");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await enqueueProcess(
        serviceId,
        adminToken,
        {
          process_name: body.process_name,
          entity_type: body.entity_type,
          entity_id: Number(body.entity_id),
          payload: body.payload || {},
          mode: body.mode || "async",
          actor: body.actor,
        },
        body.idempotency_key,
      );
      setResponseJson(pretty(res));
    } catch (err) {
      if (isSessionExpiredError(err)) {
        redirectToLogin();
        return;
      }
      if (err instanceof ApiRequestError) {
        setResponseJson(
          pretty({ status: err.status, error: err.message, body: err.body }),
        );
        setError(err.message);
      } else {
        handleErr(err);
      }
    } finally {
      setBusy(false);
    }
  }

  async function onEntitySnapshot() {
    const eid = Number(entityId);
    if (!entityType.trim() || !Number.isFinite(eid)) {
      setError("Укажите entity_type и entity_id.");
      return;
    }
    if (!entityActorId.trim()) {
      setError("Для Snapshot укажите actor_id (кто смотрит сущность).");
      return;
    }
    let params: Record<string, unknown> = {};
    try {
      params = JSON.parse(entityParams || "{}") as Record<string, unknown>;
    } catch {
      setError("params: невалидный JSON");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await entitySnapshot(
        serviceId,
        adminToken,
        entityType.trim(),
        eid,
        {
          actor: {
            actor_type: entityActorType.trim() || "user",
            actor_id: entityActorId.trim(),
            channel: "api",
          },
          params,
          include_actions: true,
        },
      );
      setResponseJson(pretty(res));
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setResponseJson(
          pretty({ status: err.status, error: err.message, body: err.body }),
        );
        setError(err.message);
      } else {
        handleErr(err);
      }
    } finally {
      setBusy(false);
    }
  }

  async function onEntityActions() {
    const eid = Number(entityId);
    if (!entityType.trim() || !Number.isFinite(eid)) {
      setError("Укажите entity_type и entity_id.");
      return;
    }
    let payload: Record<string, unknown> = {};
    try {
      payload = JSON.parse(entityPayload || "{}") as Record<string, unknown>;
    } catch {
      setError("payload: невалидный JSON");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await entityActions(
        serviceId,
        adminToken,
        entityType.trim(),
        eid,
        {
          payload,
          actor: {
            actor_type: entityActorType.trim() || "user",
            actor_id: entityActorId.trim() || undefined,
            channel: "api",
          },
        },
      );
      setResponseJson(pretty(res));
    } catch (err) {
      handleErr(err);
    } finally {
      setBusy(false);
    }
  }

  async function onEntityHistory() {
    const eid = Number(entityId);
    if (!entityType.trim() || !Number.isFinite(eid)) {
      setError("Укажите entity_type и entity_id.");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await entityHistory(
        serviceId,
        adminToken,
        entityType.trim(),
        eid,
        { limit: 50 },
      );
      setResponseJson(pretty(res));
    } catch (err) {
      handleErr(err);
    } finally {
      setBusy(false);
    }
  }

  async function onInstanceStatus() {
    const iid = Number(instanceId);
    if (!Number.isFinite(iid) || iid < 1) {
      setError("Укажите instance_id.");
      return;
    }
    setBusy(true);
    setError(null);
    setResponseJson("");
    try {
      const res = await instanceStatus(serviceId, adminToken, iid);
      setResponseJson(pretty(res));
    } catch (err) {
      handleErr(err);
    } finally {
      setBusy(false);
    }
  }

  async function onListEvents() {
    setBusy(true);
    setError(null);
    try {
      const res = await listEvents(serviceId, adminToken, {
        after_id: Number(eventsAfterId) || 0,
        limit: Number(eventsLimit) || 50,
      });
      setEventsJson(pretty(res));
      const next = (res as { next_after_id?: number }).next_after_id;
      if (next != null) setEventsAfterId(String(next));
    } catch (err) {
      handleErr(err);
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

  const commands =
    catalog?.operations.filter((o) => o.kind === "command") || [];
  const queries = catalog?.operations.filter((o) => o.kind === "query") || [];

  return (
    <main className="page">
      <div className="dash dash-wide">
        <header className="dash-top">
          <div>
            <h1 className="dash-brand">Операции</h1>
            <p className="cabinet-sid">
              <code>{serviceId}</code>
              {catalog ? (
                <> · ready: {catalog.domain_ready ? "yes" : "no"}</>
              ) : null}
            </p>
          </div>
          <div className="toolbar" style={{ marginBottom: 0 }}>
            {mode === "operations" ? (
              <button
                type="button"
                className="btn btn-ghost"
                disabled={busy}
                onClick={reloadCatalog}
              >
                Refresh catalog
              </button>
            ) : null}
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => router.push("/dashboard")}
            >
              ← ЛК
            </button>
          </div>
        </header>

        <div className="playground">
          <aside className="playground-nav">
            <div className="nav-group">
              <button
                type="button"
                className={mode === "operations" ? "nav-mode active" : "nav-mode"}
                onClick={() => {
                  setMode("operations");
                  setError(null);
                }}
              >
                Operations
              </button>
              {mode === "operations" ? (
                <div className="nav-sub">
                  <button
                    type="button"
                    className={
                      opsAction === "invoke"
                        ? "nav-sub-item active"
                        : "nav-sub-item"
                    }
                    onClick={() => {
                      setOpsAction("invoke");
                      setSelection(null);
                      setResponseJson("");
                      setError(null);
                    }}
                  >
                    Invoke
                  </button>
                  <button
                    type="button"
                    className={
                      opsAction === "enqueue"
                        ? "nav-sub-item active"
                        : "nav-sub-item"
                    }
                    onClick={() => {
                      setOpsAction("enqueue");
                      setSelection(null);
                      setResponseJson("");
                      setError(null);
                    }}
                  >
                    Enqueue
                  </button>
                </div>
              ) : null}
            </div>
            <button
              type="button"
              className={mode === "entities" ? "nav-mode active" : "nav-mode"}
              onClick={() => {
                setMode("entities");
                setError(null);
                setResponseJson("");
              }}
            >
              Entity inspect
            </button>
            <button
              type="button"
              className={mode === "events" ? "nav-mode active" : "nav-mode"}
              onClick={() => {
                setMode("events");
                setError(null);
              }}
            >
              Events
            </button>

            {mode === "operations" ? (
              <div className="playground-tree nested-tree">
                <h3>Catalog</h3>
                {!catalog && busy ? <p className="muted">Загрузка…</p> : null}
                {catalog && opsAction === "invoke" ? (
                  <>
                    <div className="tree-group">
                      <div className="tree-group-title">commands</div>
                      {commands.map((op) => (
                        <button
                          key={op.operation}
                          type="button"
                          className={
                            selection?.kind === "operation" &&
                            selection.name === op.operation
                              ? "tree-item active"
                              : "tree-item"
                          }
                          onClick={() =>
                            selectOperation(op.operation, op.kind)
                          }
                        >
                          {op.operation}
                        </button>
                      ))}
                    </div>
                    <div className="tree-group">
                      <div className="tree-group-title">queries</div>
                      {queries.map((op) => (
                        <button
                          key={op.operation}
                          type="button"
                          className={
                            selection?.kind === "operation" &&
                            selection.name === op.operation
                              ? "tree-item active"
                              : "tree-item"
                          }
                          onClick={() =>
                            selectOperation(op.operation, op.kind)
                          }
                        >
                          {op.operation}
                        </button>
                      ))}
                    </div>
                  </>
                ) : null}
                {catalog && opsAction === "enqueue" ? (
                  <div className="tree-group">
                    <div className="tree-group-title">processes</div>
                    {(catalog.processes || []).map((name) => (
                      <button
                        key={name}
                        type="button"
                        className={
                          selection?.kind === "process" &&
                          selection.name === name
                            ? "tree-item active"
                            : "tree-item"
                        }
                        onClick={() => selectProcess(name)}
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </aside>

          <section className="playground-main">
            {mode === "operations" ? (
              <>
                <div className="playground-meta">
                  {selection?.kind === "operation" ? (
                    <span>
                      <strong>{selection.name}</strong> · {selection.opKind}
                    </span>
                  ) : selection?.kind === "process" ? (
                    <span>
                      <strong>{selection.name}</strong> · process
                    </span>
                  ) : (
                    <span className="muted">
                      {opsAction === "invoke"
                        ? "Выберите command или query"
                        : "Выберите process"}
                    </span>
                  )}
                  {opsAction === "invoke" ? (
                    <button
                      type="button"
                      className="btn btn-accent"
                      style={{ minWidth: "8rem" }}
                      disabled={busy || selection?.kind !== "operation"}
                      onClick={onInvoke}
                    >
                      Invoke
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="btn btn-primary"
                      style={{ width: "auto", minWidth: "8rem" }}
                      disabled={busy || selection?.kind !== "process"}
                      onClick={onEnqueue}
                    >
                      Enqueue
                    </button>
                  )}
                </div>
                <div className="playground-panes playground-panes-stack">
                  <div className="playground-pane playground-pane-full">
                    <label htmlFor="request-json">request</label>
                    <textarea
                      id="request-json"
                      className="code-area code-area-lg"
                      value={requestJson}
                      onChange={(e) => setRequestJson(e.target.value)}
                      spellCheck={false}
                    />
                  </div>
                  <div className="playground-pane playground-pane-full">
                    <label>response</label>
                    <pre className="code-pre code-pre-lg">
                      {responseJson || "// Ответ появится здесь"}
                    </pre>
                  </div>
                </div>
              </>
            ) : null}

            {mode === "entities" ? (
              <>
                <div className="playground-meta">
                  <span>
                    Entity inspect — snapshot / actions / history / instance
                  </span>
                </div>
                <p className="muted" style={{ marginTop: 0, marginBottom: "0.85rem" }}>
                  Snapshot: access policy + карточка сущности (+ available
                  actions). Нужен <code>actor_id</code> — от чьего имени
                  смотрим.
                </p>
                <div className="tile-form" style={{ maxWidth: "100%" }}>
                  <div className="field-row">
                    <div className="field">
                      <label htmlFor="ent-type">entity_type</label>
                      <input
                        id="ent-type"
                        value={entityType}
                        onChange={(e) => setEntityType(e.target.value)}
                        placeholder="order"
                      />
                    </div>
                    <div className="field">
                      <label htmlFor="ent-id">entity_id</label>
                      <input
                        id="ent-id"
                        value={entityId}
                        onChange={(e) => setEntityId(e.target.value)}
                      />
                    </div>
                    <div className="field">
                      <label htmlFor="inst-id">instance_id</label>
                      <input
                        id="inst-id"
                        value={instanceId}
                        onChange={(e) => setInstanceId(e.target.value)}
                        placeholder="для status"
                      />
                    </div>
                  </div>
                  <div className="field-row">
                    <div className="field">
                      <label htmlFor="ent-actor-id">actor_id</label>
                      <input
                        id="ent-actor-id"
                        value={entityActorId}
                        onChange={(e) => setEntityActorId(e.target.value)}
                        placeholder="обязателен для Snapshot"
                      />
                    </div>
                    <div className="field">
                      <label htmlFor="ent-actor-type">actor_type</label>
                      <input
                        id="ent-actor-type"
                        value={entityActorType}
                        onChange={(e) => setEntityActorType(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="field">
                    <label htmlFor="ent-params">params (для snapshot)</label>
                    <textarea
                      id="ent-params"
                      className="code-area"
                      value={entityParams}
                      onChange={(e) => setEntityParams(e.target.value)}
                      spellCheck={false}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="ent-payload">payload (для actions)</label>
                    <textarea
                      id="ent-payload"
                      className="code-area"
                      value={entityPayload}
                      onChange={(e) => setEntityPayload(e.target.value)}
                      spellCheck={false}
                    />
                  </div>
                  <div className="toolbar">
                    <button
                      type="button"
                      className="btn btn-accent"
                      style={{ minWidth: "8rem" }}
                      disabled={busy}
                      onClick={onEntitySnapshot}
                    >
                      Snapshot
                    </button>
                    <button
                      type="button"
                      className="btn btn-primary"
                      style={{ width: "auto" }}
                      disabled={busy}
                      onClick={onEntityActions}
                    >
                      Actions
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      disabled={busy}
                      onClick={onEntityHistory}
                    >
                      History
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      disabled={busy}
                      onClick={onInstanceStatus}
                    >
                      Instance status
                    </button>
                  </div>
                </div>
                <div className="playground-pane playground-pane-full" style={{ marginTop: "1rem" }}>
                  <label>response</label>
                  <pre className="code-pre code-pre-lg">
                    {responseJson || "// Результат появится здесь"}
                  </pre>
                </div>
              </>
            ) : null}

            {mode === "events" ? (
              <>
                <div className="playground-meta">
                  <span>Events monitor · cursor poll</span>
                  <button
                    type="button"
                    className="btn btn-accent"
                    style={{ minWidth: "8rem" }}
                    disabled={busy}
                    onClick={onListEvents}
                  >
                    Load
                  </button>
                </div>
                <div className="field-row">
                  <div className="field">
                    <label htmlFor="ev-after">after_id</label>
                    <input
                      id="ev-after"
                      value={eventsAfterId}
                      onChange={(e) => setEventsAfterId(e.target.value)}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="ev-limit">limit</label>
                    <input
                      id="ev-limit"
                      value={eventsLimit}
                      onChange={(e) => setEventsLimit(e.target.value)}
                    />
                  </div>
                </div>
                <p className="muted" style={{ marginTop: 0 }}>
                  После Load <code>after_id</code> сдвигается на последний id в
                  ответе — удобно для поллинга.
                </p>
                <pre className="code-pre code-pre-lg">
                  {eventsJson || "// События появятся здесь"}
                </pre>
              </>
            ) : null}
          </section>
        </div>

        {error ? <div className="msg msg-error">{error}</div> : null}
      </div>
    </main>
  );
}
