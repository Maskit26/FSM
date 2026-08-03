"use client";

import { FormEvent, ReactNode, useCallback, useEffect, useState } from "react";
import { createPortal } from "react-dom";
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
  inboundHookSecretKey,
  inboundHookUrl,
  isSessionExpiredError,
  listAdminTokens,
  listEvents,
  listSchedules,
  listSecrets,
  listWebhooks,
  logout,
  pauseSchedule,
  PlatformEventItem,
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

const TILE_LABELS: Record<Exclude<TileId, null>, string> = {
  secret: "Secret",
  domain: "Domain",
  worker: "Worker",
  token: "Token",
  input: "Input",
  output: "Output",
  schedule: "Schedules",
};

const BTN_TIPS = {
  listSecrets:
    "Запрашивает у платформы список имён секретов домена без самих значений. Так можно проверить, какие ключи уже записаны (contract, graph, Telegram и др.). Значения не возвращаются — только имена. Удобно перед upsert или после онбординга.",
  upsertSecret:
    "Сохраняет или обновляет секрет в platform DB под выбранным ключом. Значение шифруется и доступно только runtime платформы и worker. После смены contract/graph URL обычно нужен reload или рестарт. Не используйте поле для пароля учётной записи ЛК.",
  deleteSecret:
    "Удаляет секрет с этим ключом из domain_secrets. После удаления связанные интеграции (graph, Telegram, contract) перестанут читать это значение. Действие необратимо — при необходимости запишите ключ заново через Upsert.",
  registerDomain:
    "Открывает страницу регистрации/онбординга домена. Там задаются cartridge и дальнейшие шаги до connect. Используйте, если домен ещё не заведён или нужно пройти сценарий заново. Из модалки это навигация, а не API-вызов connect.",
  connectDomain:
    "Запускает connect: bootstrap catalog, Domain Validator и поднятие dedicated worker. Нужны заранее записанные secrets (contract, graph). При ошибках валидации tenant останется не ready (503). Повторный connect безопасен после исправления конфига.",
  reloadCatalog:
    "Перечитывает catalog у уже запущенного domain service и сверяет его с графом. Не перезапускает процесс uvicorn на :8100 — только registries на стороне платформы. Полезно после деплоя handlers без рестарта домена. Graph SQL и ProcessDef должны совпасть.",
  graphPublish:
    "Публикует новую версию FSM-графа в domain DB (graph write). Старые instance могут остаться на прежней graph_version до завершения. Подтверждение обязательно — ошибка в графе ломает переходы. Делайте после осмысленного изменения transitions/states.",
  workerStatus:
    "Показывает текущий статус dedicated worker для вашего service_id. Видно, жив ли процесс, который claim’ит instances, timers и outbox. Если status пустой или ошибка — сначала проверьте connect. Ответ выводится JSON-ом ниже кнопок.",
  workerRestart:
    "Перезапускает worker через provisioner (local/systemd/docker/k8s). Нужен, если воркер завис, упал или после смены secrets/конфига. Кратковременно обработка очереди остановится. Не путайте с рестартом domain service.",
  workerStop:
    "Останавливает worker для этого service_id. Очередь instances и timers больше не обрабатывается, пока снова не сделаете restart или connect. Используйте при обслуживании или отладке. Domain API при этом может оставаться доступным.",
  createToken:
    "Выпускает новый DOMAIN_ADMIN_TOKEN для tenant account. Raw-значение показывается один раз — сохраните его. Токен нужен для Domain API: secrets, connect, worker, webhooks. Старые токены остаются активными, пока их не revoke.",
  listTokens:
    "Загружает список активных admin-токенов (без полного raw). Можно выбрать запись для Revoke/Rotate. Prefix помогает отличить токены друг от друга. Отозванные в список обычно не попадают.",
  revokeToken:
    "Отзывает выбранный токен — им больше нельзя вызывать Domain API. Нужно выбрать токен в списке ниже. Текущая сессия ЛК может продолжить работу, если использует другой сохранённый токен. Действие необратимо.",
  rotateToken:
    "Отзывает выбранный токен и сразу выпускает новый. Новый raw показывается в поле выше — обновите его в клиентах и в session ЛК. Удобно при компрометации или плановой ротации. Без выбранного токена кнопка неактивна.",
  getTelegramLink:
    "Строит deep-link Telegram для привязки указанного user_id к домену. Пользователь открывает ссылку в боте — платформа принимает webhook и отдаёт bind в domain operation. Нужны secrets TELEGRAM_* и зарегистрированный bind_telegram. URL ссылки появится ниже после успеха.",
  listWebhooks:
    "Показывает зарегистрированные outbound webhooks домена. По ним платформа доставляет notify из outbox. Проверьте active/off и URL перед отладкой доставки. Список обновляется после create/deactivate.",
  createWebhook:
    "Регистрирует новый outbound endpoint с HMAC-секретом. Платформа будет подписывать исходящие notify этим секретом. URL должен быть доступен из среды платформы. После создания обновите List, чтобы увидеть запись.",
  deactivateWebhook:
    "Деактивирует webhook — новые notify на этот URL больше не уходят. История доставки не очищается автоматически. При необходимости создайте новый webhook с другим URL/секретом. Неактивные записи остаются в списке со статусом off.",
  listSchedules:
    "Загружает периодические расписания enqueue для домена. Видны process_name, interval и статус ACTIVE/PAUSED. Worker сам сдвигает next_run_at. Используйте перед pause/resume или после create.",
  createSchedule:
    "Создаёт периодический запуск указанного process_name с interval_seconds. Worker при наступлении next_run_at ставит instance в очередь. Process должен быть в catalog. Слишком маленький interval нагружает очередь без нужды.",
  pauseSchedule:
    "Ставит расписание на паузу — worker перестаёт enqueue по этому id. Само расписание и interval сохраняются. Возобновить можно кнопкой Resume. Удобно на время инцидента или обслуживания процесса.",
  resumeSchedule:
    "Снимает паузу с расписания и снова включает периодический enqueue. next_run_at пересчитается по политике платформы. Убедитесь, что process и worker в порядке. После resume снова смотрите List для статуса.",
} as const;

function Tip({
  text,
  children,
}: {
  text: string;
  children: ReactNode;
}) {
  const [box, setBox] = useState<{
    left: number;
    top: number;
    above: boolean;
  } | null>(null);

  function show(el: HTMLElement) {
    const r = el.getBoundingClientRect();
    const width = Math.min(300, window.innerWidth - 24);
    let left = r.left + r.width / 2;
    left = Math.max(
      width / 2 + 8,
      Math.min(left, window.innerWidth - width / 2 - 8),
    );
    const spaceBelow = window.innerHeight - r.bottom;
    const above = spaceBelow < 140 && r.top > spaceBelow;
    setBox({
      left,
      top: above ? r.top - 10 : r.bottom + 10,
      above,
    });
  }

  function hide() {
    setBox(null);
  }

  return (
    <span
      className="tip-wrap"
      onMouseEnter={(e) => show(e.currentTarget)}
      onMouseLeave={hide}
      onFocus={(e) => show(e.currentTarget)}
      onBlur={hide}
    >
      {children}
      {box
        ? createPortal(
            <span
              className={`tip-bubble${box.above ? " tip-bubble-above" : ""}`}
              role="tooltip"
              style={{ left: box.left, top: box.top }}
            >
              {text}
            </span>,
            document.body,
          )
        : null}
    </span>
  );
}

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
  const [inputPanel, setInputPanel] = useState<"menu" | "telegram" | "generic">(
    "menu",
  );

  const [domainReady, setDomainReady] = useState<boolean | null>(null);
  const [domainError, setDomainError] = useState<string | null>(null);
  const [domainCheckedAt, setDomainCheckedAt] = useState<string | null>(null);
  const [domainStats, setDomainStats] = useState<Record<string, unknown>>({});
  const [domainWarnings, setDomainWarnings] = useState<
    { code?: string; message?: string; where?: string }[]
  >([]);
  const [processNames, setProcessNames] = useState<string[]>([]);
  const [opsCount, setOpsCount] = useState(0);
  const [hooksCount, setHooksCount] = useState(0);
  const [workerLive, setWorkerLive] = useState<string | null>(null);

  const [liveEvents, setLiveEvents] = useState<PlatformEventItem[]>([]);
  const [eventsCursor, setEventsCursor] = useState(0);
  const [eventsPaused, setEventsPaused] = useState(false);
  const [eventsError, setEventsError] = useState<string | null>(null);

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

  useEffect(() => {
    if (!openTile) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") closeTile();
    }
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [openTile]);

  const refreshDomainHealth = useCallback(async () => {
    if (!serviceId || !adminToken) return;
    try {
      const cat = await fetchCatalog(serviceId, adminToken);
      setDomainReady(!!cat.domain_ready);
      const boot = cat.domain_bootstrap || {};
      setDomainError(
        typeof boot.error === "string" && boot.error ? boot.error : null,
      );
      setDomainCheckedAt(
        typeof boot.checked_at === "string" ? boot.checked_at : null,
      );
      setDomainStats(
        boot.stats && typeof boot.stats === "object"
          ? (boot.stats as Record<string, unknown>)
          : {},
      );
      setDomainWarnings(Array.isArray(boot.warnings) ? boot.warnings : []);
      setProcessNames(cat.processes || []);
      setOpsCount((cat.operations || []).length);
      setHooksCount((cat.hooks || []).length);
      setHookChannels(cat.hooks || []);
    } catch (err) {
      setDomainReady(false);
      setDomainError(
        err instanceof Error ? err.message : "Не удалось загрузить catalog",
      );
    }
    try {
      const ws = await workerStatus(serviceId, adminToken);
      setWorkerLive(ws.status || "unknown");
    } catch {
      setWorkerLive("unavailable");
    }
  }, [serviceId, adminToken]);

  // Один последовательный цикл: не бьём catalog/events/worker параллельно —
  // platform DB pool маленький (Clever ~5 conn), иначе QueuePool → 500.
  useEffect(() => {
    if (!ready || !serviceId || !adminToken) return;
    let cancelled = false;
    const cursorRef = { current: eventsCursor };
    let seeded = liveEvents.length > 0;
    let tickN = 0;

    async function pullEvents() {
      if (eventsPaused) return;
      try {
        const res = !seeded
          ? await listEvents(serviceId, adminToken, {
              newest: true,
              limit: 40,
            })
          : await listEvents(serviceId, adminToken, {
              after_id: cursorRef.current,
              limit: 50,
            });
        if (cancelled) return;
        const items = res.items || [];
        if (!seeded) {
          setLiveEvents(items.slice().reverse());
          seeded = true;
        } else if (items.length) {
          setLiveEvents((prev) => {
            const merged = [...items.slice().reverse(), ...prev];
            return merged.slice(0, 80);
          });
        }
        if (res.next_after_id != null) {
          cursorRef.current = Number(res.next_after_id) || cursorRef.current;
          setEventsCursor(cursorRef.current);
        }
        setEventsError(null);
      } catch (err) {
        if (!cancelled) {
          setEventsError(
            err instanceof Error ? err.message : "Ошибка загрузки events",
          );
        }
      }
    }

    async function cycle() {
      if (cancelled || inFlight) return;
      inFlight = true;
      try {
        // health ~ каждые 15с при интервале 5с
        if (tickN % 3 === 0) {
          await refreshDomainHealth();
        }
        tickN += 1;
        if (!cancelled) await pullEvents();
      } finally {
        inFlight = false;
      }
    }

    let inFlight = false;
    void cycle();
    const t = window.setInterval(() => {
      void cycle();
    }, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- seed cursor once per mount/pause
  }, [ready, serviceId, adminToken, eventsPaused, refreshDomainHealth]);

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

  function closeTile() {
    clearMsg();
    setOpenTile(null);
    setInputPanel("menu");
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
      await refreshDomainHealth();
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
      await refreshDomainHealth();
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
      setInputPanel("menu");
      return;
    }
    setOpenTile("input");
    setInputPanel("menu");
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
          </div>
        ) : null}

        <div className="tile-grid">
          <button
            type="button"
            className="tile"
            onClick={() => router.push("/playground")}
          >
            <span className="tile-title">Operations</span>
            <span className="tile-sub">
              Песочница для вызовов catalog, invoke и enqueue по живому домену.
              Можно выбрать сущность и событие, посмотреть ответ платформы и
              проверить, как отрабатывает FSM без отдельного клиента.
            </span>
          </button>
          <button
            type="button"
            className="tile"
            onClick={() => router.push("/e2e")}
          >
            <span className="tile-title">E2E</span>
            <span className="tile-sub">
              Запуск YAML-сценариев против подключенного домена прямо из браузера.
              Шаги выполняются локально, отчёт можно скачать. Удобно для
              регрессии онбординга и ключевых бизнес-флоу.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "secret" ? " tile-open" : ""}`}
            onClick={() => toggleTile("secret")}
          >
            <span className="tile-title">Secret</span>
            <span className="tile-sub">
              Управление секретами домена в platform DB: contract URL, graph
              credentials, Telegram и прочие ключи. Значения шифруются и не
              отдаются обратно при листинге — только имена ключей.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "domain" ? " tile-open" : ""}`}
            onClick={() => toggleTile("domain")}
          >
            <span className="tile-title">Domain</span>
            <span className="tile-sub">
              Жизненный цикл домена: регистрация, connect, reload catalog и
              работа с графом. Здесь проверяете готовность tenant после
              bootstrap и синхронизацию ProcessDef с SQL-переходами.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "worker" ? " tile-open" : ""}`}
            onClick={() => toggleTile("worker")}
          >
            <span className="tile-title">Worker</span>
            <span className="tile-sub">
              Управление выделенным FSM-worker для вашего service_id. Смотрите
              статус, перезапускайте или останавливайте процесс, который claim’ит
              instances, timers и outbox.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "token" ? " tile-open" : ""}`}
            onClick={() => toggleTile("token")}
          >
            <span className="tile-title">Token</span>
            <span className="tile-sub">
              Выпуск и просмотр DOMAIN_ADMIN_TOKEN для вызовов Domain API.
              Токен привязан к вашему tenant account и нужен для secrets,
              connect и остальных admin-операций домена.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "input" ? " tile-open" : ""}`}
            onClick={() => onOpenInput()}
          >
            <span className="tile-title">Input</span>
            <span className="tile-sub">
              Входящие каналы снаружи: Telegram и универсальный Generic webhook
              для любых партнёров. Guided setup и свой channel в каталоге домена.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "output" ? " tile-open" : ""}`}
            onClick={() => toggleTile("output")}
          >
            <span className="tile-title">Output</span>
            <span className="tile-sub">
              Исходящие уведомления и webhooks из platform outbox. Создавайте
              endpoints, куда платформа доставляет notify после команд и
              эффектов FSM.
            </span>
          </button>
          <button
            type="button"
            className={`tile${openTile === "schedule" ? " tile-open" : ""}`}
            onClick={() => toggleTile("schedule")}
          >
            <span className="tile-title">Schedules</span>
            <span className="tile-sub">
              Периодический enqueue процессов по интервалу. Создавайте,
              ставьте на паузу и возобновляйте расписания — worker сам сдвинет
              next_run_at и поставит instance в очередь.
            </span>
          </button>
        </div>

        <div className="monitors-row">
          <section className="monitor-panel domain-monitor" aria-label="Статус домена">
            <div className="monitor-head">
              <h2>Статус домена</h2>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ width: "auto" }}
                onClick={() => void refreshDomainHealth()}
              >
                Обновить
              </button>
            </div>
            <div className="health-grid">
              <div className={`health-chip${domainReady ? " ok" : domainReady === false ? " bad" : ""}`}>
                <span className="health-label">Ready</span>
                <strong>
                  {domainReady == null ? "…" : domainReady ? "да" : "нет"}
                </strong>
              </div>
              <div className="health-chip">
                <span className="health-label">Worker</span>
                <strong>{workerLive || "…"}</strong>
              </div>
              <div className="health-chip">
                <span className="health-label">Processes</span>
                <strong>{processNames.length}</strong>
              </div>
              <div className="health-chip">
                <span className="health-label">Operations</span>
                <strong>{opsCount}</strong>
              </div>
              <div className="health-chip">
                <span className="health-label">Hooks</span>
                <strong>{hooksCount}</strong>
              </div>
              <div className="health-chip">
                <span className="health-label">Transitions</span>
                <strong>
                  {domainStats.transitions_scanned != null
                    ? String(domainStats.transitions_scanned)
                    : "—"}
                </strong>
              </div>
            </div>
            {domainCheckedAt ? (
              <p className="muted monitor-meta">
                Проверка: {domainCheckedAt}
                {domainStats.guards != null ? ` · guards ${String(domainStats.guards)}` : ""}
                {domainStats.effects != null ? ` · effects ${String(domainStats.effects)}` : ""}
              </p>
            ) : null}
            {domainError ? (
              <div className="msg msg-error" style={{ marginTop: "0.75rem" }}>
                {domainError}
              </div>
            ) : null}
            {domainWarnings.length > 0 ? (
              <ul className="warn-list">
                {domainWarnings.map((w, i) => (
                  <li key={`${w.code || "w"}-${i}`}>
                    <code>{w.code || "WARNING"}</code>
                    <span>{w.message || "—"}</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </section>

          <section className="monitor-panel events-monitor" aria-label="События домена">
            <div className="monitor-head">
              <h2>События</h2>
              <div className="monitor-actions">
                <span className="muted monitor-meta">
                  {eventsPaused ? "пауза" : "live · 5с"}
                  {liveEvents.length ? ` · ${liveEvents.length}` : ""}
                </span>
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ width: "auto" }}
                  onClick={() => setEventsPaused((p) => !p)}
                >
                  {eventsPaused ? "Продолжить" : "Пауза"}
                </button>
              </div>
            </div>
            {eventsError ? (
              <div className="msg msg-error" style={{ marginBottom: "0.75rem" }}>
                {eventsError}
              </div>
            ) : null}
            {liveEvents.length === 0 && !eventsError ? (
              <p className="muted">Пока нет событий — появятся при работе домена.</p>
            ) : (
              <ul className="events-feed">
                {liveEvents.map((ev) => (
                  <li key={ev.id} className="event-row">
                    <span className="event-id">#{ev.id}</span>
                    <span className="event-type">{ev.event_type || "—"}</span>
                    <span className="event-meta">
                      {ev.entity_type || "—"}
                      {ev.entity_id != null ? `/${ev.entity_id}` : ""}
                      {ev.instance_id != null ? ` · inst ${ev.instance_id}` : ""}
                    </span>
                    <time className="event-time" dateTime={ev.created_at || undefined}>
                      {ev.created_at
                        ? new Date(ev.created_at).toLocaleString()
                        : ""}
                    </time>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        {openTile ? (
          <div
            className="modal-backdrop"
            role="presentation"
            onClick={closeTile}
          >
            <div
              className="modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="tile-modal-title"
              onClick={(e) => e.stopPropagation()}
            >
              <header className="modal-head">
                <h2 id="tile-modal-title">{TILE_LABELS[openTile]}</h2>
                <button
                  type="button"
                  className="btn btn-ghost modal-close"
                  onClick={closeTile}
                  aria-label="Закрыть"
                >
                  Закрыть
                </button>
              </header>
              <div className="modal-body">
                {openTile === "secret" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.listSecrets}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListSecrets}>
                          List
                        </button>
                      </Tip>
                    </div>
                    <form className="tile-form" onSubmit={onUpsertSecret} autoComplete="off">
                      <div className="field">
                        <label htmlFor="sec-key">Key</label>
                        <input
                          id="sec-key"
                          name="fsm_secret_key"
                          value={secretKey}
                          onChange={(e) => setSecretKey(e.target.value)}
                          autoComplete="off"
                          required
                        />
                      </div>
                      <div className="field">
                        <label htmlFor="sec-val">Value</label>
                        <input
                          id="sec-val"
                          name="fsm_secret_value"
                          type="password"
                          value={secretValue}
                          onChange={(e) => setSecretValue(e.target.value)}
                          autoComplete="new-password"
                          required
                        />
                      </div>
                      <Tip text={BTN_TIPS.upsertSecret}>
                        <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                          Upsert
                        </button>
                      </Tip>
                    </form>
                    {secretKeys.length > 0 ? (
                      <ul className="plain-list">
                        {secretKeys.map((k) => (
                          <li key={k}>
                            <code>{k}</code>
                            <Tip text={BTN_TIPS.deleteSecret}>
                              <button
                                type="button"
                                className="btn btn-danger"
                                disabled={busy}
                                onClick={() => onDeleteSecret(k)}
                              >
                                Delete
                              </button>
                            </Tip>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </>
                ) : null}

                {openTile === "domain" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.registerDomain}>
                        <button
                          type="button"
                          className="btn btn-ghost"
                          onClick={() => router.push("/domain-registration")}
                        >
                          Register
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.connectDomain}>
                        <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onDomainConnect}>
                          Connect
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.reloadCatalog}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onDomainReload}>
                          Reload catalog
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.graphPublish}>
                        <button type="button" className="btn btn-danger" disabled={busy} onClick={onGraphPublish}>
                          Graph publish
                        </button>
                      </Tip>
                    </div>
                    {domainResult ? (
                      <div className="probe-panel">
                        <pre>{domainResult}</pre>
                      </div>
                    ) : null}
                  </>
                ) : null}

                {openTile === "worker" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.workerStatus}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onWorkerStatus}>
                          Status
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.workerRestart}>
                        <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onWorkerRestart}>
                          Restart
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.workerStop}>
                        <button type="button" className="btn btn-danger" disabled={busy} onClick={onWorkerStop}>
                          Stop
                        </button>
                      </Tip>
                    </div>
                    {workerInfo ? (
                      <div className="probe-panel">
                        <pre>{workerInfo}</pre>
                      </div>
                    ) : null}
                  </>
                ) : null}

                {openTile === "token" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.createToken}>
                        <button type="button" className="btn btn-primary" style={{ width: "auto" }} disabled={busy} onClick={onCreateToken}>
                          Create
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.listTokens}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListTokens}>
                          List
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.revokeToken}>
                        <button type="button" className="btn btn-danger" disabled={busy || selectedTokenId == null} onClick={onRevokeToken}>
                          Revoke
                        </button>
                      </Tip>
                      <Tip text={BTN_TIPS.rotateToken}>
                        <button type="button" className="btn btn-ghost" disabled={busy || selectedTokenId == null} onClick={onRotateToken}>
                          Rotate
                        </button>
                      </Tip>
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
                  </>
                ) : null}

                {openTile === "input" ? (
                  <>
                    {inputPanel === "menu" ? (
                      <>
                        <p className="muted" style={{ marginTop: 0 }}>
                          Выберите входящий канал: Telegram или универсальный
                          Generic webhook.
                        </p>
                        <div className="input-channel-grid">
                          <button
                            type="button"
                            className="input-channel-card"
                            onClick={() => setInputPanel("telegram")}
                          >
                            <strong>Telegram</strong>
                            <span>
                              Webhook Update и deep-link привязки аккаунта.
                              Платформа сама разбирает протокол бота.
                            </span>
                          </button>
                          <button
                            type="button"
                            className="input-channel-card"
                            onClick={() => setInputPanel("generic")}
                          >
                            <strong>Generic webhook</strong>
                            <span>
                              Универсальный вход для внешних партнёров. Домен
                              регистрирует channel, партнёр бьёт в URL с секретом.
                            </span>
                          </button>
                        </div>
                      </>
                    ) : null}

                    {inputPanel === "telegram" ? (
                      <>
                        <div className="toolbar" style={{ justifyContent: "flex-start" }}>
                          <button
                            type="button"
                            className="btn btn-ghost"
                            onClick={() => setInputPanel("menu")}
                          >
                            ← Каналы
                          </button>
                        </div>
                        <ol className="wizard-steps">
                          <li>
                            Положите в Secret ключи{" "}
                            <code>TELEGRAM_BOT_TOKEN</code>,{" "}
                            <code>TELEGRAM_BOT_USERNAME</code>, опц.{" "}
                            <code>TELEGRAM_LINK_SECRET</code>.
                          </li>
                          <li>
                            В BotFather / setWebhook укажите URL ниже.
                          </li>
                          <li>
                            В домене зарегистрируйте command{" "}
                            <code>bind_telegram</code>.
                          </li>
                          <li>Проверьте deep-link для user_id.</li>
                        </ol>
                        <div className="field">
                          <label>Telegram webhook URL</label>
                          <div className="token-box">{telegramWebhookUrl(serviceId)}</div>
                        </div>
                        <form className="tile-form" onSubmit={onTelegramLink} autoComplete="off">
                          <div className="field">
                            <label htmlFor="tg-uid">user_id → deep-link</label>
                            <input
                              id="tg-uid"
                              name="fsm_telegram_user_id"
                              value={telegramUserId}
                              onChange={(e) => setTelegramUserId(e.target.value)}
                              autoComplete="off"
                              required
                            />
                          </div>
                          <Tip text={BTN_TIPS.getTelegramLink}>
                            <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                              Get link
                            </button>
                          </Tip>
                        </form>
                        {telegramLinkUrl ? (
                          <div className="token-box" style={{ marginTop: "0.75rem" }}>
                            {telegramLinkUrl}
                          </div>
                        ) : null}
                      </>
                    ) : null}

                    {inputPanel === "generic" ? (
                      <>
                        <div className="toolbar" style={{ justifyContent: "flex-start" }}>
                          <button
                            type="button"
                            className="btn btn-ghost"
                            onClick={() => setInputPanel("menu")}
                          >
                            ← Каналы
                          </button>
                        </div>
                        <ol className="wizard-steps">
                          <li>
                            В домене:{" "}
                            <code>hooks.register(service_id, &quot;payment&quot;, handler)</code>{" "}
                            и перезапуск domain + Reload catalog.
                          </li>
                          <li>
                            В Secret сохраните{" "}
                            <code>INPUT_HOOK_SECRET_PAYMENT</code> (или общий{" "}
                            <code>INPUT_HOOK_SECRET</code>).
                          </li>
                          <li>
                            Партнёру отдайте URL канала и заголовок{" "}
                            <code>X-Input-Secret</code> (либо HMAC{" "}
                            <code>X-Input-Timestamp</code> +{" "}
                            <code>X-Input-Signature</code>).
                          </li>
                          <li>
                            В handler разберите payload провайдера и верните
                            enqueue / notify при необходимости.
                          </li>
                        </ol>
                        <h3 style={{ margin: "1rem 0 0.5rem", fontSize: "1rem" }}>
                          Каналы из catalog
                        </h3>
                        {hookChannels.length === 0 ? (
                          <p className="muted">
                            Пока пусто: зарегистрируйте hook в домене и сделайте
                            Reload catalog.
                          </p>
                        ) : (
                          <ul className="plain-list">
                            {hookChannels.map((ch) => (
                              <li key={ch} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.35rem" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", flexWrap: "wrap" }}>
                                  <code>{ch}</code>
                                  <span className="meta">секрет: {inboundHookSecretKey(ch)}</span>
                                </div>
                                <span className="meta" style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem", wordBreak: "break-all" }}>
                                  {inboundHookUrl(serviceId, ch)}
                                </span>
                              </li>
                            ))}
                          </ul>
                        )}
                        <p className="muted" style={{ marginBottom: 0, fontSize: "0.82rem" }}>
                          Шаблон:{" "}
                          <code>{inboundHookUrl(serviceId, "{channel}")}</code>
                        </p>
                      </>
                    ) : null}
                  </>
                ) : null}

                {openTile === "output" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.listWebhooks}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListWebhooks}>
                          List webhooks
                        </button>
                      </Tip>
                    </div>
                    <form className="tile-form" onSubmit={onCreateWebhook} autoComplete="off">
                      <div className="field">
                        <label htmlFor="hook-url">URL</label>
                        <input
                          id="hook-url"
                          name="fsm_webhook_url"
                          value={hookUrl}
                          onChange={(e) => setHookUrl(e.target.value)}
                          autoComplete="off"
                          required
                        />
                      </div>
                      <div className="field">
                        <label htmlFor="hook-secret">Secret (HMAC)</label>
                        <input
                          id="hook-secret"
                          name="fsm_webhook_secret"
                          type="password"
                          value={hookSecret}
                          onChange={(e) => setHookSecret(e.target.value)}
                          autoComplete="new-password"
                          required
                        />
                      </div>
                      <Tip text={BTN_TIPS.createWebhook}>
                        <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                          Create webhook
                        </button>
                      </Tip>
                    </form>
                    {webhooks.length > 0 ? (
                      <ul className="plain-list">
                        {webhooks.map((w) => (
                          <li key={w.id}>
                            <span>
                              #{w.id} · {w.active ? "active" : "off"} · {w.url}
                            </span>
                            {w.active ? (
                              <Tip text={BTN_TIPS.deactivateWebhook}>
                                <button
                                  type="button"
                                  className="btn btn-danger"
                                  disabled={busy}
                                  onClick={() => onDeactivateWebhook(w.id)}
                                >
                                  Deactivate
                                </button>
                              </Tip>
                            ) : null}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </>
                ) : null}

                {openTile === "schedule" ? (
                  <>
                    <div className="toolbar">
                      <Tip text={BTN_TIPS.listSchedules}>
                        <button type="button" className="btn btn-ghost" disabled={busy} onClick={onListSchedules}>
                          List
                        </button>
                      </Tip>
                    </div>
                    <form className="tile-form" onSubmit={onCreateSchedule} autoComplete="off">
                      <div className="field">
                        <label htmlFor="sched-proc">process_name</label>
                        <input
                          id="sched-proc"
                          name="fsm_schedule_process"
                          value={schedProcess}
                          onChange={(e) => setSchedProcess(e.target.value)}
                          autoComplete="off"
                          required
                        />
                      </div>
                      <div className="field">
                        <label htmlFor="sched-int">interval_seconds</label>
                        <input
                          id="sched-int"
                          name="fsm_schedule_interval"
                          type="number"
                          min={1}
                          value={schedInterval}
                          onChange={(e) => setSchedInterval(e.target.value)}
                          autoComplete="off"
                          required
                        />
                      </div>
                      <Tip text={BTN_TIPS.createSchedule}>
                        <button type="submit" className="btn btn-primary" style={{ width: "auto" }} disabled={busy}>
                          Create
                        </button>
                      </Tip>
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
                              <Tip text={BTN_TIPS.pauseSchedule}>
                                <button
                                  type="button"
                                  className="btn btn-ghost"
                                  disabled={busy}
                                  onClick={() => onPauseSchedule(s.id)}
                                >
                                  Pause
                                </button>
                              </Tip>
                              <Tip text={BTN_TIPS.resumeSchedule}>
                                <button
                                  type="button"
                                  className="btn btn-ghost"
                                  disabled={busy}
                                  onClick={() => onResumeSchedule(s.id)}
                                >
                                  Resume
                                </button>
                              </Tip>
                            </span>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </>
                ) : null}

                {error ? (
                  <div className="msg msg-error" style={{ marginTop: "1rem" }}>
                    {error}
                  </div>
                ) : null}
                {info ? (
                  <div className="msg msg-ok" style={{ marginTop: "1rem" }}>
                    {info}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}

        {!openTile && error ? <div className="msg msg-error">{error}</div> : null}
        {!openTile && info ? <div className="msg msg-ok">{info}</div> : null}
      </div>
    </main>
  );
}
