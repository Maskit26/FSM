"""SQL-запросы только к платформенной БД. Сессии создаёт и владеет ими воркер или Request Runtime."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


SessionLike = Session | Connection


class FsmDbLayer:
    """Слой персистентности платформы: состояния сущностей, логи переходов, таймеры и вспомогательные таблицы."""

    # --- entity_fsm_state ---

    def get_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        *,
        for_update: bool = False,
    ) -> Optional[str]:
        """Возвращает текущее FSM-состояние сущности из entity_fsm_state.
        for_update=True — SELECT … FOR UPDATE (сериализация apply по сущности).
        """
        lock = " FOR UPDATE" if for_update else ""
        row = session.execute(
            text(
                f"""
                SELECT current_state
                FROM entity_fsm_state
                WHERE service_id = :service_id
                  AND entity_type = :entity_type
                  AND entity_id = :entity_id
                {lock}
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
            },
        ).mappings().first()
        return None if row is None else str(row["current_state"])

    def upsert_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        """Создаёт или обновляет запись состояния сущности (INSERT … ON DUPLICATE KEY UPDATE).
        Для переходов FSM используй cas_entity_state — upsert безусловен и гонкоопасен.
        """
        session.execute(
            text(
                """
                INSERT INTO entity_fsm_state
                    (service_id, entity_type, entity_id, current_state, updated_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :current_state, UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    current_state = VALUES(current_state),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
            },
        )

    def delete_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
    ) -> bool:
        """Удаляет строку entity_fsm_state. True если была удалена."""
        result = session.execute(
            text(
                """
                DELETE FROM entity_fsm_state
                WHERE service_id = :service_id
                  AND entity_type = :entity_type
                  AND entity_id = :entity_id
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": int(entity_id),
            },
        )
        return int(result.rowcount or 0) > 0

    def cas_entity_state(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        *,
        from_state: str,
        to_state: str,
    ) -> bool:
        """
        Атомарно: current_state = from_state → to_state.
        True только если строка обновлена (CAS успешен).
        """
        result = session.execute(
            text(
                """
                UPDATE entity_fsm_state
                SET current_state = :to_state,
                    updated_at = UTC_TIMESTAMP()
                WHERE service_id = :service_id
                  AND entity_type = :entity_type
                  AND entity_id = :entity_id
                  AND current_state = :from_state
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
            },
        )
        return int(result.rowcount or 0) == 1

    def insert_entity_state_initial(
        self,
        session: SessionLike,
        service_id: str,
        entity_type: str,
        entity_id: int,
        current_state: str,
    ) -> None:
        """Вставляет начальное состояние сущности без upsert. Применяется при первичной инициализации FSM для новой сущности."""
        session.execute(
            text(
                """
                INSERT INTO entity_fsm_state
                    (service_id, entity_type, entity_id, current_state, updated_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :current_state, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
            },
        )

    # --- fsm_transition_logs ---

    def insert_transition_log(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        from_state: str,
        to_state: str,
        event_name: str,
        transition_id: int,
        instance_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        """Записывает факт перехода в fsm_transition_logs для аудита и диагностики. Вызывается при каждом успешном apply без идемпотентности."""
        session.execute(
            text(
                """
                INSERT INTO fsm_transition_logs
                    (service_id, entity_type, entity_id, from_state, to_state,
                     event_name, transition_id, instance_id, user_id, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :from_state, :to_state,
                     :event_name, :transition_id, :instance_id, :user_id, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "instance_id": instance_id,
                "user_id": user_id,
            },
        )

    def insert_transition_log_idempotent(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        from_state: str,
        to_state: str,
        event_name: str,
        transition_id: int,
        instance_id: int,
        user_id: Optional[int] = None,
    ) -> bool:
        """Вставляет лог перехода с INSERT IGNORE по паре (instance_id, transition_id). Возвращает True, если запись создана; False при повторной обработке."""
        result = session.execute(
            text(
                """
                INSERT IGNORE INTO fsm_transition_logs
                    (service_id, entity_type, entity_id, from_state, to_state,
                     event_name, transition_id, instance_id, user_id, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :from_state, :to_state,
                     :event_name, :transition_id, :instance_id, :user_id, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "instance_id": instance_id,
                "user_id": user_id,
            },
        )
        return bool(result.rowcount and result.rowcount > 0)

    # --- fsm_timers ---

    def insert_timer(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        process_name: str,
        fire_at: datetime,
        payload: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        owner: str = "domain",
    ) -> int:
        """
        Планирует отложенный запуск процесса в fsm_timers (SCHEDULED).
        owner: domain | platform (чья политика таймера). Нужна миграция 006.
        """
        owner_n = str(owner or "domain").strip().lower()
        if owner_n not in ("domain", "platform"):
            owner_n = "domain"
        result = session.execute(
            text(
                """
                INSERT INTO fsm_timers
                    (service_id, entity_type, entity_id, process_name, fire_at,
                     status, payload_json, idempotency_key, owner, created_at)
                VALUES
                    (:service_id, :entity_type, :entity_id, :process_name, :fire_at,
                     'SCHEDULED', :payload_json, :idempotency_key, :owner, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "process_name": process_name,
                "fire_at": fire_at,
                "payload_json": json.dumps(payload) if payload is not None else None,
                "idempotency_key": idempotency_key,
                "owner": owner_n,
            },
        )
        return int(result.lastrowid)

    def cancel_timer(self, session: SessionLike, timer_id: int) -> None:
        """Отменяет запланированный таймер, если он ещё в статусе SCHEDULED. Используется при досрочном прекращении отложенного процесса."""
        session.execute(
            text(
                """
                UPDATE fsm_timers
                SET status = 'CANCELLED', cancelled_at = UTC_TIMESTAMP()
                WHERE id = :timer_id AND status = 'SCHEDULED'
                """
            ),
            {"timer_id": timer_id},
        )

    def cancel_timer_by_idempotency_key(
        self, session: SessionLike, service_id: str, idempotency_key: str
    ) -> int:
        """Отмена SCHEDULED-таймера по idempotency_key. Возвращает число строк."""
        result = session.execute(
            text(
                """
                UPDATE fsm_timers
                SET status = 'CANCELLED', cancelled_at = UTC_TIMESTAMP()
                WHERE service_id = :service_id
                  AND idempotency_key = :idempotency_key
                  AND status = 'SCHEDULED'
                """
            ),
            {"service_id": service_id, "idempotency_key": idempotency_key},
        )
        return int(result.rowcount or 0)

    def claim_due_timers(
        self,
        session: SessionLike,
        *,
        limit: int = 20,
        service_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Забирает due SCHEDULED таймеры (fire_at <= UTC now) и помечает FIRED.
        Возвращает строки для enqueue процессов.
        service_id — опциональный фильтр тенанта (воркер на одного арендатора).
        """
        svc_sql = "AND service_id = :service_id" if service_id else ""
        params: dict[str, Any] = {"limit": int(limit)}
        if service_id:
            params["service_id"] = service_id
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, entity_type, entity_id, process_name,
                       payload_json
                FROM fsm_timers
                WHERE status = 'SCHEDULED'
                  AND fire_at <= UTC_TIMESTAMP()
                  {svc_sql}
                ORDER BY fire_at ASC
                LIMIT :limit
                FOR UPDATE SKIP LOCKED
                """
            ),
            params,
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            session.execute(
                text(
                    """
                    UPDATE fsm_timers
                    SET status = 'FIRED'
                    WHERE id = :id AND status = 'SCHEDULED'
                    """
                ),
                {"id": int(item["id"])},
            )
            raw = item.get("payload_json")
            if isinstance(raw, str) and raw.strip():
                try:
                    item["payload"] = json.loads(raw)
                except json.JSONDecodeError:
                    item["payload"] = {}
            elif isinstance(raw, dict):
                item["payload"] = raw
            else:
                item["payload"] = {}
            out.append(item)
        return out

    # --- server_fsm_instances ---

    def insert_fsm_instance(
        self,
        session: SessionLike,
        *,
        service_id: str,
        process_name: str,
        entity_type: str,
        entity_id: int,
        payload: Optional[dict[str, Any]] = None,
        actor_id: Optional[int] = None,
        graph_version: Optional[int] = None,
    ) -> int:
        """Создаёт PENDING server_fsm_instances. actor_id — opaque id из Public API actor (не колонка домена)."""
        has_gv = self._has_column(session, "server_fsm_instances", "graph_version")
        if has_gv:
            result = session.execute(
                text(
                    """
                    INSERT INTO server_fsm_instances
                        (service_id, process_name, entity_type, entity_id, status,
                         attempts, payload_json, actor_id, graph_version,
                         created_at, updated_at)
                    VALUES
                        (:service_id, :process_name, :entity_type, :entity_id, 'PENDING',
                         0, :payload_json, :actor_id, :graph_version,
                         UTC_TIMESTAMP(), UTC_TIMESTAMP())
                    """
                ),
                {
                    "service_id": service_id,
                    "process_name": process_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "payload_json": json.dumps(payload or {}),
                    "actor_id": actor_id,
                    "graph_version": graph_version,
                },
            )
        else:
            result = session.execute(
                text(
                    """
                    INSERT INTO server_fsm_instances
                        (service_id, process_name, entity_type, entity_id, status,
                         attempts, payload_json, actor_id,
                         created_at, updated_at)
                    VALUES
                        (:service_id, :process_name, :entity_type, :entity_id, 'PENDING',
                         0, :payload_json, :actor_id, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                    """
                ),
                {
                    "service_id": service_id,
                    "process_name": process_name,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "payload_json": json.dumps(payload or {}),
                    "actor_id": actor_id,
                },
            )
        return int(result.lastrowid)

    def get_fsm_instance(
        self,
        session: SessionLike,
        service_id: str,
        instance_id: int,
    ) -> Optional[dict[str, Any]]:
        """Загружает экземпляр FSM по id и service_id. Нужен для статуса, диагностики и повторной обработки."""
        gv = (
            ", graph_version"
            if self._has_column(session, "server_fsm_instances", "graph_version")
            else ""
        )
        row = session.execute(
            text(
                f"""
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, last_error, payload_json, actor_id
                       {gv}, created_at, started_at, finished_at
                FROM server_fsm_instances
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {"id": instance_id, "service_id": service_id},
        ).mappings().first()
        return dict(row) if row else None

    def get_fsm_instance_by_id(
        self, session: SessionLike, instance_id: int
    ) -> Optional[dict[str, Any]]:
        """Загружает instance по id (без service_id). Для saga heal/fan-in."""
        gv = (
            ", graph_version"
            if self._has_column(session, "server_fsm_instances", "graph_version")
            else ""
        )
        row = session.execute(
            text(
                f"""
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, last_error, payload_json, actor_id
                       {gv}, created_at, started_at, finished_at
                FROM server_fsm_instances
                WHERE id = :id
                """
            ),
            {"id": instance_id},
        ).mappings().first()
        return dict(row) if row else None

    def claim_pending_instance(
        self,
        session: SessionLike,
        *,
        service_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Атомарно захватывает старейший due PENDING (FOR UPDATE SKIP LOCKED) → PROCESSING.
        service_id — опциональный фильтр тенанта (воркер на одного арендатора).
        """
        gv = (
            ", graph_version"
            if self._has_column(session, "server_fsm_instances", "graph_version")
            else ""
        )
        svc_sql = "AND service_id = :service_id" if service_id else ""
        params: dict[str, Any] = {}
        if service_id:
            params["service_id"] = service_id
        row = session.execute(
            text(
                f"""
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, payload_json, actor_id{gv}
                FROM server_fsm_instances
                WHERE status = 'PENDING'
                  AND (next_attempt_at IS NULL
                       OR next_attempt_at <= UTC_TIMESTAMP())
                  {svc_sql}
                ORDER BY id ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
                """
            ),
            params,
        ).mappings().first()
        if row is None:
            return None
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'PROCESSING',
                    started_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": row["id"]},
        )
        return dict(row)

    def mark_instance_completed(
        self, session: SessionLike, instance_id: int
    ) -> None:
        """Помечает экземпляр COMPLETED и фиксирует время завершения. Вызывается после успешного шага TransitionRunner."""
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'COMPLETED', finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP(), last_error = NULL,
                    next_attempt_at = NULL
                WHERE id = :id
                """
            ),
            {"id": instance_id},
        )

    def mark_instance_failed(
        self,
        session: SessionLike,
        instance_id: int,
        last_error: str,
        *,
        attempts: Optional[int] = None,
    ) -> None:
        """Терминальный FAILED. attempts — итоговое значение; иначе attempts+1."""
        if attempts is None:
            session.execute(
                text(
                    """
                    UPDATE server_fsm_instances
                    SET status = 'FAILED', last_error = :err,
                        finished_at = UTC_TIMESTAMP(),
                        updated_at = UTC_TIMESTAMP(),
                        attempts = attempts + 1,
                        next_attempt_at = NULL
                    WHERE id = :id
                    """
                ),
                {"id": instance_id, "err": (last_error or "")[:2000]},
            )
            return
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'FAILED', last_error = :err,
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP(),
                    attempts = :attempts,
                    next_attempt_at = NULL
                WHERE id = :id
                """
            ),
            {
                "id": instance_id,
                "err": (last_error or "")[:2000],
                "attempts": int(attempts),
            },
        )

    def mark_instance_retry(
        self,
        session: SessionLike,
        instance_id: int,
        *,
        last_error: str,
        attempts: int,
        backoff_seconds: int,
    ) -> None:
        """Возвращает инстанс в PENDING с next_attempt_at (временная ошибка)."""
        session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'PENDING',
                    last_error = :err,
                    attempts = :attempts,
                    next_attempt_at = DATE_ADD(
                        UTC_TIMESTAMP(), INTERVAL :backoff SECOND
                    ),
                    finished_at = NULL,
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {
                "id": int(instance_id),
                "err": (last_error or "")[:2000],
                "attempts": int(attempts),
                "backoff": int(backoff_seconds),
            },
        )

    def list_pending_instances(
        self,
        session: SessionLike,
        *,
        service_id: str,
        process_name: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """PENDING-инстансы сервиса (опц. фильтр process_name). Для domain recovery."""
        params: dict[str, Any] = {
            "service_id": service_id,
            "lim": int(limit),
        }
        proc_sql = ""
        if process_name:
            proc_sql = "AND process_name = :process_name"
            params["process_name"] = process_name
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, process_name, entity_type, entity_id,
                       status, attempts, payload_json, actor_id
                FROM server_fsm_instances
                WHERE service_id = :service_id
                  AND status = 'PENDING'
                  {proc_sql}
                ORDER BY id ASC
                LIMIT :lim
                """
            ),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]

    def mark_instance_cancelled(
        self,
        session: SessionLike,
        instance_id: int,
        *,
        last_error: str = "CANCELLED",
    ) -> bool:
        """PENDING|PROCESSING → CANCELLED. True если строка обновлена."""
        result = session.execute(
            text(
                """
                UPDATE server_fsm_instances
                SET status = 'CANCELLED',
                    last_error = :err,
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP(),
                    next_attempt_at = NULL
                WHERE id = :id
                  AND status IN ('PENDING', 'PROCESSING')
                """
            ),
            {"id": int(instance_id), "err": (last_error or "CANCELLED")[:2000]},
        )
        return int(result.rowcount or 0) == 1

    # --- platform_reconcile_queue ---

    def enqueue_reconcile(
        self,
        session: SessionLike,
        *,
        service_id: str,
        instance_id: int,
        entity_type: Optional[str],
        entity_id: Optional[int],
        from_state: Optional[str],
        to_state: Optional[str],
        event_name: Optional[str],
        transition_id: Optional[int],
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        """Ставит задачу сверки платформы и домена в platform_reconcile_queue. Нужна для асинхронного восстановления после частичных сбоев."""
        session.execute(
            text(
                """
                INSERT INTO platform_reconcile_queue
                    (service_id, instance_id, entity_type, entity_id,
                     from_state, to_state, event_name, transition_id,
                     payload_json, status, attempts, created_at, updated_at)
                VALUES
                    (:service_id, :instance_id, :entity_type, :entity_id,
                     :from_state, :to_state, :event_name, :transition_id,
                     :payload_json, 'PENDING', 0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    status = IF(status = 'DONE', status, 'PENDING'),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": service_id,
                "instance_id": instance_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "from_state": from_state,
                "to_state": to_state,
                "event_name": event_name,
                "transition_id": transition_id,
                "payload_json": json.dumps(payload or {}),
            },
        )

    def claim_pending_reconcile(
        self,
        session: SessionLike,
        *,
        limit: int = 10,
        service_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """PENDING reconcile → PROCESSING (FOR UPDATE SKIP LOCKED).
        service_id — опциональный фильтр тенанта.
        """
        svc_sql = "AND service_id = :service_id" if service_id else ""
        params: dict[str, Any] = {"lim": int(limit)}
        if service_id:
            params["service_id"] = service_id
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, instance_id, entity_type, entity_id,
                       from_state, to_state, event_name, transition_id,
                       payload_json, attempts
                FROM platform_reconcile_queue
                WHERE status = 'PENDING'
                  {svc_sql}
                ORDER BY id ASC
                LIMIT :lim
                FOR UPDATE SKIP LOCKED
                """
            ),
            params,
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            session.execute(
                text(
                    """
                    UPDATE platform_reconcile_queue
                    SET status = 'PROCESSING',
                        attempts = attempts + 1,
                        updated_at = UTC_TIMESTAMP()
                    WHERE id = :id AND status = 'PENDING'
                    """
                ),
                {"id": int(item["id"])},
            )
            raw = item.get("payload_json")
            if isinstance(raw, str) and raw.strip():
                try:
                    item["payload"] = json.loads(raw)
                except json.JSONDecodeError:
                    item["payload"] = {}
            elif isinstance(raw, dict):
                item["payload"] = raw
            else:
                item["payload"] = {}
            out.append(item)
        return out

    def mark_reconcile_done(self, session: SessionLike, reconcile_id: int) -> None:
        """Успешный докат platform."""
        session.execute(
            text(
                """
                UPDATE platform_reconcile_queue
                SET status = 'DONE',
                    done_at = UTC_TIMESTAMP(),
                    last_error = NULL,
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": int(reconcile_id)},
        )

    def mark_reconcile_retry(
        self,
        session: SessionLike,
        reconcile_id: int,
        *,
        error: str,
        dead: bool = False,
    ) -> None:
        """Ошибка доката → PENDING (retry) или DEAD."""
        status = "DEAD" if dead else "PENDING"
        session.execute(
            text(
                """
                UPDATE platform_reconcile_queue
                SET status = :status,
                    last_error = :err,
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {
                "id": int(reconcile_id),
                "status": status,
                "err": (error or "")[:2000],
            },
        )

    # --- idempotency_keys ---

    def get_idempotency(
        self,
        session: SessionLike,
        *,
        service_id: str,
        scope: str,
        key: str,
    ) -> Optional[dict[str, Any]]:
        """Lookup Idempotency-Key. None если нет или истёк."""
        row = session.execute(
            text(
                """
                SELECT service_id, scope, `key`, instance_id, response_json,
                       created_at, expires_at
                FROM idempotency_keys
                WHERE service_id = :service_id
                  AND scope = :scope
                  AND `key` = :key
                  AND (expires_at IS NULL OR expires_at > UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "scope": scope,
                "key": key,
            },
        ).mappings().first()
        if row is None:
            return None
        item = dict(row)
        raw = item.get("response_json")
        if isinstance(raw, str) and raw.strip():
            try:
                item["response"] = json.loads(raw)
            except json.JSONDecodeError:
                item["response"] = {}
        elif isinstance(raw, dict):
            item["response"] = raw
        else:
            item["response"] = {}
        return item

    def put_idempotency(
        self,
        session: SessionLike,
        *,
        service_id: str,
        scope: str,
        key: str,
        response: dict[str, Any],
        instance_id: Optional[int] = None,
        ttl_hours: int = 24,
    ) -> bool:
        """
        Сохраняет ответ для повтора. True если вставлено, False если ключ уже был
        (INSERT IGNORE — гонка двух одинаковых запросов).
        """
        result = session.execute(
            text(
                """
                INSERT IGNORE INTO idempotency_keys
                    (service_id, scope, `key`, instance_id, response_json,
                     created_at, expires_at)
                VALUES
                    (:service_id, :scope, :key, :instance_id, :response_json,
                     UTC_TIMESTAMP(),
                     DATE_ADD(UTC_TIMESTAMP(), INTERVAL :ttl HOUR))
                """
            ),
            {
                "service_id": service_id,
                "scope": scope,
                "key": key,
                "instance_id": instance_id,
                "response_json": json.dumps(response or {}),
                "ttl": int(ttl_hours),
            },
        )
        return int(result.rowcount or 0) > 0

    # --- platform_outbox / platform_events ---

    def insert_outbox(
        self,
        session: SessionLike,
        *,
        service_id: str,
        channel: str,
        destination: str,
        event_type: str,
        payload: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> int:
        """Добавляет исходящее сообщение в platform_outbox для надёжной доставки. Возвращает id записи outbox.
        Дубликат idempotency_key → 0 (без ошибки транзакции).
        """
        result = session.execute(
            text(
                """
                INSERT IGNORE INTO platform_outbox
                    (service_id, channel, destination, event_type, payload_json,
                     status, attempts, next_attempt_at, idempotency_key, created_at)
                VALUES
                    (:service_id, :channel, :destination, :event_type, :payload_json,
                     'PENDING', 0, UTC_TIMESTAMP(), :idempotency_key, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "channel": channel,
                "destination": destination,
                "event_type": event_type,
                "payload_json": json.dumps(payload or {}),
                "idempotency_key": idempotency_key,
            },
        )
        if int(result.rowcount or 0) == 0:
            return 0
        return int(result.lastrowid)

    def claim_pending_outbox(
        self,
        session: SessionLike,
        *,
        limit: int = 10,
        service_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Берёт PENDING outbox строки (FOR UPDATE SKIP LOCKED) → PROCESSING.
        Возвращает список dict с полями строки.
        service_id — опциональный фильтр тенанта.
        """
        svc_sql = "AND service_id = :service_id" if service_id else ""
        params: dict[str, Any] = {"lim": int(limit)}
        if service_id:
            params["service_id"] = service_id
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, channel, destination, event_type,
                       payload_json, attempts, idempotency_key
                FROM platform_outbox
                WHERE status = 'PENDING'
                  AND next_attempt_at <= UTC_TIMESTAMP()
                  {svc_sql}
                ORDER BY id ASC
                LIMIT :lim
                FOR UPDATE SKIP LOCKED
                """
            ),
            params,
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            session.execute(
                text(
                    """
                    UPDATE platform_outbox
                    SET status = 'PROCESSING', attempts = attempts + 1
                    WHERE id = :id AND status = 'PENDING'
                    """
                ),
                {"id": int(item["id"])},
            )
            out.append(item)
        return out

    def mark_outbox_sent(self, session: SessionLike, outbox_id: int) -> None:
        """Успешная доставка."""
        session.execute(
            text(
                """
                UPDATE platform_outbox
                SET status = 'SENT', sent_at = UTC_TIMESTAMP(), last_error = NULL
                WHERE id = :id
                """
            ),
            {"id": int(outbox_id)},
        )

    def mark_outbox_retry(
        self,
        session: SessionLike,
        outbox_id: int,
        *,
        error: str,
        backoff_seconds: int,
        dead: bool = False,
    ) -> None:
        """Ошибка доставки: PENDING + backoff или DEAD."""
        status = "DEAD" if dead else "PENDING"
        session.execute(
            text(
                """
                UPDATE platform_outbox
                SET status = :status,
                    last_error = :err,
                    next_attempt_at = DATE_ADD(
                        UTC_TIMESTAMP(), INTERVAL :backoff SECOND
                    )
                WHERE id = :id
                """
            ),
            {
                "id": int(outbox_id),
                "status": status,
                "err": (error or "")[:2000],
                "backoff": int(max(1, backoff_seconds)),
            },
        )

    def insert_event(
        self,
        session: SessionLike,
        *,
        service_id: str,
        event_type: str,
        instance_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        payload: Optional[dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        client_request_id: Optional[str] = None,
    ) -> int:
        """Записывает платформенное событие в platform_events для аудита и трассировки. Возвращает id созданного события."""
        result = session.execute(
            text(
                """
                INSERT INTO platform_events
                    (service_id, event_type, instance_id, entity_type, entity_id,
                     payload_json, correlation_id, client_request_id, created_at)
                VALUES
                    (:service_id, :event_type, :instance_id, :entity_type, :entity_id,
                     :payload_json, :correlation_id, :client_request_id, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "event_type": event_type,
                "instance_id": instance_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "payload_json": json.dumps(payload or {}),
                "correlation_id": correlation_id,
                "client_request_id": client_request_id,
            },
        )
        return int(result.lastrowid)

    def latest_event_id(
        self, session: SessionLike, *, service_id: str
    ) -> int:
        """MAX(id) в platform_events для service (0 если пусто)."""
        row = session.execute(
            text(
                """
                SELECT COALESCE(MAX(id), 0) AS mid
                FROM platform_events
                WHERE service_id = :service_id
                """
            ),
            {"service_id": service_id},
        ).mappings().fetchone()
        return int((row or {}).get("mid") or 0)

    def list_events_after(
        self,
        session: SessionLike,
        *,
        service_id: str,
        after_id: int = 0,
        limit: int = 100,
        newest: bool = False,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        События platform_events.
        newest=False: id > after_id ASC (cursor poll).
        newest=True: последние N (DESC→ASC) для монитора ЛК.
        Опционально фильтр entity_type / entity_id (entity WS).
        """
        lim = int(max(1, min(limit, 500)))
        et = str(entity_type or "").strip() or None
        eid = int(entity_id) if entity_id is not None else None
        entity_sql = ""
        params: dict[str, Any] = {"service_id": service_id, "limit": lim}
        if et is not None:
            entity_sql += " AND entity_type = :entity_type"
            params["entity_type"] = et
        if eid is not None:
            entity_sql += " AND entity_id = :entity_id"
            params["entity_id"] = eid
        if newest:
            rows = session.execute(
                text(
                    f"""
                    SELECT id, service_id, event_type, instance_id,
                           entity_type, entity_id, payload_json,
                           correlation_id, client_request_id, created_at
                    FROM (
                        SELECT id, service_id, event_type, instance_id,
                               entity_type, entity_id, payload_json,
                               correlation_id, client_request_id, created_at
                        FROM platform_events
                        WHERE service_id = :service_id
                          {entity_sql}
                        ORDER BY id DESC
                        LIMIT :limit
                    ) AS recent
                    ORDER BY id ASC
                    """
                ),
                params,
            ).mappings().all()
        else:
            params["after_id"] = int(after_id)
            rows = session.execute(
                text(
                    f"""
                    SELECT id, service_id, event_type, instance_id,
                           entity_type, entity_id, payload_json,
                           correlation_id, client_request_id, created_at
                    FROM platform_events
                    WHERE service_id = :service_id
                      AND id > :after_id
                      {entity_sql}
                    ORDER BY id ASC
                    LIMIT :limit
                    """
                ),
                params,
            ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            raw = item.get("payload_json")
            if isinstance(raw, str) and raw.strip():
                try:
                    item["payload"] = json.loads(raw)
                except json.JSONDecodeError:
                    item["payload"] = {}
            elif isinstance(raw, dict):
                item["payload"] = raw
            else:
                item["payload"] = {}
            item.pop("payload_json", None)
            created = item.get("created_at")
            if hasattr(created, "isoformat"):
                item["created_at"] = created.isoformat()
            out.append(item)
        return out

    def list_transition_logs(
        self,
        session: SessionLike,
        *,
        service_id: str,
        entity_type: str,
        entity_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """История переходов сущности из fsm_transition_logs (новые сверху)."""
        params: dict[str, Any] = {
            "service_id": service_id,
            "entity_type": entity_type,
            "entity_id": int(entity_id),
            "limit": int(max(1, min(limit, 200))),
        }
        before_sql = ""
        if before_id is not None:
            before_sql = "AND id < :before_id"
            params["before_id"] = int(before_id)
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, entity_type, entity_id,
                       from_state, to_state, event_name, transition_id,
                       instance_id, user_id, created_at
                FROM fsm_transition_logs
                WHERE service_id = :service_id
                  AND entity_type = :entity_type
                  AND entity_id = :entity_id
                  {before_sql}
                ORDER BY id DESC
                LIMIT :limit
                """
            ),
            params,
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            created = item.get("created_at")
            if hasattr(created, "isoformat"):
                item["created_at"] = created.isoformat()
            out.append(item)
        return out

    # --- fsm_sagas ---

    def insert_saga(
        self,
        session: SessionLike,
        *,
        service_id: str,
        fail_policy: str = "fail_fast",
        on_success: Optional[dict[str, Any]] = None,
        on_fail: Optional[dict[str, Any]] = None,
        payload: Optional[dict[str, Any]] = None,
        actor_id: Optional[int] = None,
    ) -> int:
        """Создаёт RUNNING saga. Возвращает saga_id."""
        result = session.execute(
            text(
                """
                INSERT INTO fsm_sagas
                    (service_id, status, fail_policy, on_success_json, on_fail_json,
                     payload_json, actor_id, created_at, updated_at)
                VALUES
                    (:service_id, 'RUNNING', :fail_policy, :on_success_json, :on_fail_json,
                     :payload_json, :actor_id, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "fail_policy": fail_policy,
                "on_success_json": (
                    json.dumps(on_success) if on_success is not None else None
                ),
                "on_fail_json": json.dumps(on_fail) if on_fail is not None else None,
                "payload_json": json.dumps(payload or {}),
                "actor_id": actor_id,
            },
        )
        return int(result.lastrowid)

    def insert_saga_child(
        self,
        session: SessionLike,
        *,
        saga_id: int,
        instance_id: int,
        entity_type: str,
        entity_id: int,
        process_name: str,
    ) -> int:
        """Привязывает PENDING instance к saga."""
        result = session.execute(
            text(
                """
                INSERT INTO fsm_saga_children
                    (saga_id, instance_id, entity_type, entity_id, process_name,
                     status, created_at, updated_at)
                VALUES
                    (:saga_id, :instance_id, :entity_type, :entity_id, :process_name,
                     'PENDING', UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "saga_id": saga_id,
                "instance_id": instance_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "process_name": process_name,
            },
        )
        return int(result.lastrowid)

    def get_saga(self, session: SessionLike, saga_id: int) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, service_id, status, fail_policy,
                       on_success_json, on_fail_json, payload_json, actor_id,
                       created_at, updated_at, finished_at
                FROM fsm_sagas
                WHERE id = :id
                """
            ),
            {"id": saga_id},
        ).mappings().first()
        if not row:
            return None
        item = dict(row)
        for key in ("on_success_json", "on_fail_json", "payload_json"):
            raw = item.get(key)
            if isinstance(raw, str) and raw.strip():
                try:
                    item[key.replace("_json", "")] = json.loads(raw)
                except json.JSONDecodeError:
                    item[key.replace("_json", "")] = None
            elif isinstance(raw, dict):
                item[key.replace("_json", "")] = raw
            else:
                item[key.replace("_json", "")] = None
        return item

    def get_saga_child_by_instance(
        self, session: SessionLike, instance_id: int
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, saga_id, instance_id, entity_type, entity_id,
                       process_name, status, last_error
                FROM fsm_saga_children
                WHERE instance_id = :instance_id
                """
            ),
            {"instance_id": instance_id},
        ).mappings().first()
        return dict(row) if row else None

    def mark_saga_child_terminal(
        self,
        session: SessionLike,
        instance_id: int,
        status: str,
        last_error: Optional[str] = None,
    ) -> Optional[int]:
        """
        COMPLETED|FAILED для child. Возвращает saga_id или None если не child.
        Идемпотентно: уже терминальный child не меняет status повторно.
        """
        child = self.get_saga_child_by_instance(session, instance_id)
        if child is None:
            return None
        if str(child.get("status") or "") in (
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        ):
            return int(child["saga_id"])
        session.execute(
            text(
                """
                UPDATE fsm_saga_children
                SET status = :status,
                    last_error = :err,
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE instance_id = :instance_id
                  AND status IN ('PENDING', 'RUNNING')
                """
            ),
            {
                "instance_id": instance_id,
                "status": status,
                "err": (last_error or "")[:2000] if last_error else None,
            },
        )
        return int(child["saga_id"])

    def list_saga_children(
        self, session: SessionLike, saga_id: int
    ) -> list[dict[str, Any]]:
        rows = session.execute(
            text(
                """
                SELECT id, saga_id, instance_id, entity_type, entity_id,
                       process_name, status, last_error
                FROM fsm_saga_children
                WHERE saga_id = :saga_id
                ORDER BY id ASC
                """
            ),
            {"saga_id": saga_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def cancel_pending_saga_children(
        self, session: SessionLike, saga_id: int
    ) -> list[int]:
        """CANCELLED на PENDING children + instances. Возвращает instance_ids."""
        rows = session.execute(
            text(
                """
                SELECT instance_id
                FROM fsm_saga_children
                WHERE saga_id = :saga_id AND status = 'PENDING'
                FOR UPDATE
                """
            ),
            {"saga_id": saga_id},
        ).fetchall()
        ids = [int(r[0]) for r in rows]
        if not ids:
            return []
        placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
        params: dict[str, Any] = {f"id_{i}": iid for i, iid in enumerate(ids)}
        params["saga_id"] = saga_id
        session.execute(
            text(
                f"""
                UPDATE fsm_saga_children
                SET status = 'CANCELLED',
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE saga_id = :saga_id
                  AND status = 'PENDING'
                  AND instance_id IN ({placeholders})
                """
            ),
            params,
        )
        session.execute(
            text(
                f"""
                UPDATE server_fsm_instances
                SET status = 'CANCELLED',
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP(),
                    last_error = 'SAGA_CANCELLED'
                WHERE id IN ({placeholders})
                  AND status = 'PENDING'
                """
            ),
            {f"id_{i}": iid for i, iid in enumerate(ids)},
        )
        return ids

    def cas_finish_saga(
        self, session: SessionLike, saga_id: int, status: str
    ) -> bool:
        """CAS RUNNING → SUCCEEDED|FAILED. True если эта сессия выиграла финиш."""
        result = session.execute(
            text(
                """
                UPDATE fsm_sagas
                SET status = :status,
                    finished_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id AND status = 'RUNNING'
                """
            ),
            {"id": saga_id, "status": status},
        )
        return int(result.rowcount or 0) == 1

    # --- webhook_subscriptions ---

    def list_webhook_subscriptions(
        self,
        session: SessionLike,
        *,
        service_id: str,
        active_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Активные (или все) webhook_subscriptions для service_id."""
        sql = """
            SELECT id, service_id, url, secret, event_types, active, created_at
            FROM webhook_subscriptions
            WHERE service_id = :service_id
        """
        if active_only:
            sql += " AND active = 1"
        sql += " ORDER BY id ASC"
        rows = session.execute(
            text(sql), {"service_id": service_id}
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            raw = item.get("event_types")
            if isinstance(raw, str) and raw.strip():
                try:
                    item["event_types"] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
            out.append(item)
        return out

    def get_webhook_subscription(
        self, session: SessionLike, *, service_id: str, subscription_id: int
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, service_id, url, secret, event_types, active, created_at
                FROM webhook_subscriptions
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {"id": int(subscription_id), "service_id": service_id},
        ).mappings().first()
        return dict(row) if row else None

    def insert_webhook_subscription(
        self,
        session: SessionLike,
        *,
        service_id: str,
        url: str,
        secret: str,
        event_types: Optional[list[str]] = None,
        active: bool = True,
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO webhook_subscriptions
                    (service_id, url, secret, event_types, active, created_at)
                VALUES
                    (:service_id, :url, :secret, :event_types, :active, UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "url": url,
                "secret": secret,
                "event_types": (
                    json.dumps(event_types) if event_types is not None else None
                ),
                "active": 1 if active else 0,
            },
        )
        return int(result.lastrowid)

    def set_webhook_subscription_active(
        self,
        session: SessionLike,
        *,
        service_id: str,
        subscription_id: int,
        active: bool,
    ) -> bool:
        result = session.execute(
            text(
                """
                UPDATE webhook_subscriptions
                SET active = :active
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {
                "id": int(subscription_id),
                "service_id": service_id,
                "active": 1 if active else 0,
            },
        )
        return int(result.rowcount or 0) > 0

    # --- fsm_schedules ---

    def insert_schedule(
        self,
        session: SessionLike,
        *,
        service_id: str,
        process_name: str,
        interval_seconds: int,
        entity_type: str = "schedule",
        entity_id: int = 0,
        payload: Optional[dict[str, Any]] = None,
        next_run_at: Optional[datetime] = None,
    ) -> int:
        """Создаёт ACTIVE периодический schedule."""
        result = session.execute(
            text(
                """
                INSERT INTO fsm_schedules
                    (service_id, process_name, entity_type, entity_id,
                     interval_seconds, payload_json, next_run_at, status,
                     created_at, updated_at)
                VALUES
                    (:service_id, :process_name, :entity_type, :entity_id,
                     :interval_seconds, :payload_json,
                     COALESCE(:next_run_at, UTC_TIMESTAMP()), 'ACTIVE',
                     UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "process_name": process_name,
                "entity_type": entity_type,
                "entity_id": int(entity_id),
                "interval_seconds": int(interval_seconds),
                "payload_json": json.dumps(payload or {}),
                "next_run_at": next_run_at,
            },
        )
        return int(result.lastrowid)

    def claim_due_schedules(
        self,
        session: SessionLike,
        *,
        limit: int = 20,
        service_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        ACTIVE schedules с next_run_at<=now → сдвигает next_run_at += interval.
        Возвращает snapshot строк до сдвига (для enqueue).
        service_id — опциональный фильтр тенанта.
        """
        svc_sql = "AND service_id = :service_id" if service_id else ""
        params: dict[str, Any] = {"lim": int(limit)}
        if service_id:
            params["service_id"] = service_id
        rows = session.execute(
            text(
                f"""
                SELECT id, service_id, process_name, entity_type, entity_id,
                       interval_seconds, payload_json, next_run_at, status
                FROM fsm_schedules
                WHERE status = 'ACTIVE'
                  AND next_run_at <= UTC_TIMESTAMP()
                  {svc_sql}
                ORDER BY next_run_at ASC, id ASC
                LIMIT :lim
                FOR UPDATE SKIP LOCKED
                """
            ),
            params,
        ).mappings().all()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            raw = item.get("payload_json")
            if isinstance(raw, str) and raw.strip():
                try:
                    item["payload"] = json.loads(raw)
                except json.JSONDecodeError:
                    item["payload"] = {}
            elif isinstance(raw, dict):
                item["payload"] = raw
            else:
                item["payload"] = {}
            interval = max(1, int(item.get("interval_seconds") or 60))
            session.execute(
                text(
                    """
                    UPDATE fsm_schedules
                    SET next_run_at = DATE_ADD(
                            UTC_TIMESTAMP(), INTERVAL :interval SECOND
                        ),
                        last_error = NULL,
                        updated_at = UTC_TIMESTAMP()
                    WHERE id = :id AND status = 'ACTIVE'
                    """
                ),
                {"id": int(item["id"]), "interval": interval},
            )
            out.append(item)
        return out

    def set_schedule_status(
        self,
        session: SessionLike,
        *,
        service_id: str,
        schedule_id: int,
        status: str,
    ) -> bool:
        result = session.execute(
            text(
                """
                UPDATE fsm_schedules
                SET status = :status, updated_at = UTC_TIMESTAMP()
                WHERE id = :id AND service_id = :service_id
                """
            ),
            {
                "id": int(schedule_id),
                "service_id": service_id,
                "status": status,
            },
        )
        return int(result.rowcount or 0) > 0

    def list_schedules(
        self, session: SessionLike, *, service_id: str
    ) -> list[dict[str, Any]]:
        rows = session.execute(
            text(
                """
                SELECT id, service_id, process_name, entity_type, entity_id,
                       interval_seconds, payload_json, next_run_at, status,
                       last_error, created_at, updated_at
                FROM fsm_schedules
                WHERE service_id = :service_id
                ORDER BY id ASC
                """
            ),
            {"service_id": service_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    # --- schema helpers ---

    @staticmethod
    def _has_column(session: SessionLike, table: str, column: str) -> bool:
        row = session.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = :t AND column_name = :c
                LIMIT 1
                """
            ),
            {"t": table, "c": column},
        ).first()
        return row is not None

    # --- tenant accounts and authentication ---

    def create_tenant_account(
        self, session: SessionLike, *, email: str, password_hash: str
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO tenant_accounts
                    (email, password_hash, status, created_at, updated_at)
                VALUES
                    (:email, :password_hash, 'pending_verification',
                     UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {"email": email, "password_hash": password_hash},
        )
        return int(result.lastrowid)

    def get_tenant_account_by_email(
        self, session: SessionLike, *, email: str
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, email, password_hash, status, email_verified_at,
                       failed_login_count, locked_until, created_at, updated_at
                FROM tenant_accounts
                WHERE email = :email
                LIMIT 1
                """
            ),
            {"email": email},
        ).mappings().first()
        return dict(row) if row else None

    def get_tenant_account(
        self, session: SessionLike, *, tenant_account_id: int
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, email, password_hash, status, email_verified_at,
                       failed_login_count, locked_until, created_at, updated_at
                FROM tenant_accounts
                WHERE id = :id
                LIMIT 1
                """
            ),
            {"id": int(tenant_account_id)},
        ).mappings().first()
        return dict(row) if row else None

    def create_email_verification(
        self,
        session: SessionLike,
        *,
        tenant_account_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> int:
        session.execute(
            text(
                """
                UPDATE tenant_email_verifications
                SET used_at = UTC_TIMESTAMP()
                WHERE tenant_account_id = :tenant_account_id
                  AND used_at IS NULL
                """
            ),
            {"tenant_account_id": int(tenant_account_id)},
        )
        result = session.execute(
            text(
                """
                INSERT INTO tenant_email_verifications
                    (tenant_account_id, token_hash, expires_at, created_at)
                VALUES
                    (:tenant_account_id, :token_hash, :expires_at, UTC_TIMESTAMP())
                """
            ),
            {
                "tenant_account_id": int(tenant_account_id),
                "token_hash": token_hash,
                "expires_at": expires_at,
            },
        )
        return int(result.lastrowid)

    def consume_email_verification(
        self, session: SessionLike, *, token_hash: str
    ) -> Optional[int]:
        row = session.execute(
            text(
                """
                SELECT id, tenant_account_id
                FROM tenant_email_verifications
                WHERE token_hash = :token_hash
                  AND used_at IS NULL
                  AND expires_at > UTC_TIMESTAMP()
                FOR UPDATE
                """
            ),
            {"token_hash": token_hash},
        ).mappings().first()
        if row is None:
            return None
        account_id = int(row["tenant_account_id"])
        session.execute(
            text(
                """
                UPDATE tenant_email_verifications
                SET used_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": int(row["id"])},
        )
        session.execute(
            text(
                """
                UPDATE tenant_accounts
                SET status = 'active', email_verified_at = UTC_TIMESTAMP(),
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": account_id},
        )
        return account_id

    def record_tenant_login_success(
        self, session: SessionLike, *, tenant_account_id: int
    ) -> None:
        session.execute(
            text(
                """
                UPDATE tenant_accounts
                SET failed_login_count = 0, locked_until = NULL,
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": int(tenant_account_id)},
        )

    def record_tenant_login_failure(
        self, session: SessionLike, *, tenant_account_id: int, lock_after: int = 5
    ) -> None:
        session.execute(
            text(
                """
                UPDATE tenant_accounts
                SET failed_login_count = failed_login_count + 1,
                    locked_until = CASE
                        WHEN failed_login_count + 1 >= :lock_after
                        THEN DATE_ADD(UTC_TIMESTAMP(), INTERVAL 15 MINUTE)
                        ELSE locked_until
                    END,
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :id
                """
            ),
            {"id": int(tenant_account_id), "lock_after": int(lock_after)},
        )

    # --- tenant refresh sessions ---

    def create_refresh_token(
        self,
        session: SessionLike,
        *,
        tenant_account_id: int,
        token_hash: str,
        family_id: str,
        expires_at: datetime,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO tenant_refresh_tokens
                    (tenant_account_id, token_hash, family_id, expires_at,
                     source_ip, user_agent, created_at)
                VALUES
                    (:tenant_account_id, :token_hash, :family_id, :expires_at,
                     :source_ip, :user_agent, UTC_TIMESTAMP())
                """
            ),
            {
                "tenant_account_id": int(tenant_account_id),
                "token_hash": token_hash,
                "family_id": family_id,
                "expires_at": expires_at,
                "source_ip": source_ip,
                "user_agent": user_agent,
            },
        )
        return int(result.lastrowid)

    def get_refresh_token_for_update(
        self, session: SessionLike, *, token_hash: str
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, tenant_account_id, token_hash, family_id, expires_at,
                       revoked_at, replaced_by_id, last_used_at
                FROM tenant_refresh_tokens
                WHERE token_hash = :token_hash
                LIMIT 1
                FOR UPDATE
                """
            ),
            {"token_hash": token_hash},
        ).mappings().first()
        return dict(row) if row else None

    def rotate_refresh_token(
        self,
        session: SessionLike,
        *,
        old_token_id: int,
        new_token_id: int,
    ) -> bool:
        result = session.execute(
            text(
                """
                UPDATE tenant_refresh_tokens
                SET revoked_at = UTC_TIMESTAMP(), replaced_by_id = :new_token_id,
                    last_used_at = UTC_TIMESTAMP()
                WHERE id = :old_token_id AND revoked_at IS NULL
                """
            ),
            {
                "old_token_id": int(old_token_id),
                "new_token_id": int(new_token_id),
            },
        )
        return int(result.rowcount or 0) == 1

    def revoke_refresh_family(
        self, session: SessionLike, *, family_id: str
    ) -> None:
        session.execute(
            text(
                """
                UPDATE tenant_refresh_tokens
                SET revoked_at = COALESCE(revoked_at, UTC_TIMESTAMP())
                WHERE family_id = :family_id
                """
            ),
            {"family_id": family_id},
        )

    # --- tenant-scoped DOMAIN_ADMIN_TOKEN ---

    def create_domain_admin_token(
        self,
        session: SessionLike,
        *,
        tenant_account_id: int,
        token_hash: str,
        token_prefix: str,
        name: Optional[str],
        expires_at: Optional[datetime],
    ) -> int:
        result = session.execute(
            text(
                """
                INSERT INTO domain_admin_tokens
                    (tenant_account_id, token_hash, token_prefix, name,
                     expires_at, created_at)
                VALUES
                    (:tenant_account_id, :token_hash, :token_prefix, :name,
                     :expires_at, UTC_TIMESTAMP())
                """
            ),
            {
                "tenant_account_id": int(tenant_account_id),
                "token_hash": token_hash,
                "token_prefix": token_prefix,
                "name": name,
                "expires_at": expires_at,
            },
        )
        return int(result.lastrowid)

    def get_domain_admin_token(
        self, session: SessionLike, *, token_hash: str
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT id, tenant_account_id, token_hash, token_prefix, name, expires_at,
                       revoked_at, last_used_at, created_at
                FROM domain_admin_tokens
                WHERE token_hash = :token_hash
                LIMIT 1
                """
            ),
            {"token_hash": token_hash},
        ).mappings().first()
        return dict(row) if row else None

    def list_domain_admin_tokens(
        self, session: SessionLike, *, tenant_account_id: int
    ) -> list[dict[str, Any]]:
        rows = session.execute(
            text(
                """
                SELECT id, token_prefix, name, expires_at, revoked_at,
                       last_used_at, created_at
                FROM domain_admin_tokens
                WHERE tenant_account_id = :tenant_account_id
                ORDER BY id DESC
                """
            ),
            {"tenant_account_id": int(tenant_account_id)},
        ).mappings().all()
        return [dict(row) for row in rows]

    def revoke_domain_admin_token(
        self,
        session: SessionLike,
        *,
        tenant_account_id: int,
        token_id: int,
    ) -> bool:
        result = session.execute(
            text(
                """
                UPDATE domain_admin_tokens
                SET revoked_at = COALESCE(revoked_at, UTC_TIMESTAMP())
                WHERE id = :token_id
                  AND tenant_account_id = :tenant_account_id
                """
            ),
            {
                "tenant_account_id": int(tenant_account_id),
                "token_id": int(token_id),
            },
        )
        return int(result.rowcount or 0) == 1

    def touch_domain_admin_token(
        self, session: SessionLike, *, token_id: int
    ) -> None:
        session.execute(
            text(
                """
                UPDATE domain_admin_tokens
                SET last_used_at = UTC_TIMESTAMP()
                WHERE id = :token_id
                """
            ),
            {"token_id": int(token_id)},
        )

    # --- domain ownership and audit ---

    def tenant_owns_service(
        self,
        session: SessionLike,
        *,
        tenant_account_id: int,
        service_id: str,
    ) -> bool:
        row = session.execute(
            text(
                """
                SELECT 1
                FROM domain_services
                WHERE service_id = :service_id
                  AND tenant_account_id = :tenant_account_id
                LIMIT 1
                """
            ),
            {
                "tenant_account_id": int(tenant_account_id),
                "service_id": service_id,
            },
        ).first()
        return row is not None

    def create_domain_service(
        self,
        session: SessionLike,
        *,
        service_id: str,
        tenant_account_id: int,
        cartridge_type: str,
        version: str,
        package_ref: Optional[str],
        package_checksum: Optional[str],
        db_secret_ref: str,
        db_graph_secret_ref: Optional[str],
        db_graph_write_secret_ref: Optional[str],
    ) -> None:
        session.execute(
            text(
                """
                INSERT INTO domain_services
                    (service_id, tenant_account_id, cartridge_type, version,
                     package_ref, package_checksum, db_secret_ref,
                     db_graph_secret_ref, db_graph_write_secret_ref, status,
                     created_at, updated_at)
                VALUES
                    (:service_id, :tenant_account_id, :cartridge_type, :version,
                     :package_ref, :package_checksum, :db_secret_ref,
                     :db_graph_secret_ref, :db_graph_write_secret_ref,
                     'pending_configuration', UTC_TIMESTAMP(), UTC_TIMESTAMP())
                """
            ),
            {
                "service_id": service_id,
                "tenant_account_id": int(tenant_account_id),
                "cartridge_type": cartridge_type,
                "version": version,
                "package_ref": package_ref,
                "package_checksum": package_checksum,
                "db_secret_ref": db_secret_ref,
                "db_graph_secret_ref": db_graph_secret_ref,
                "db_graph_write_secret_ref": db_graph_write_secret_ref,
            },
        )

    def set_domain_service_status(
        self,
        session: SessionLike,
        *,
        service_id: str,
        status: str,
        validation_report: Optional[str] = None,
    ) -> bool:
        result = session.execute(
            text(
                """
                UPDATE domain_services
                SET status = :status, validation_report = :validation_report,
                    updated_at = UTC_TIMESTAMP()
                WHERE service_id = :service_id
                """
            ),
            {
                "service_id": service_id,
                "status": status,
                "validation_report": validation_report,
            },
        )
        return int(result.rowcount or 0) == 1

    def get_domain_service(
        self, session: SessionLike, *, service_id: str
    ) -> Optional[dict[str, Any]]:
        row = session.execute(
            text(
                """
                SELECT service_id, tenant_account_id, cartridge_type, version,
                       package_ref, package_checksum, db_secret_ref,
                       db_graph_secret_ref, db_graph_write_secret_ref,
                       pool_options_json, status, validation_report,
                       created_at, updated_at
                FROM domain_services
                WHERE service_id = :service_id
                LIMIT 1
                """
            ),
            {"service_id": service_id},
        ).mappings().first()
        return dict(row) if row else None

    def insert_platform_audit_event(
        self,
        session: SessionLike,
        *,
        event_type: str,
        result: str,
        tenant_account_id: Optional[int] = None,
        service_id: Optional[str] = None,
        domain_admin_token_id: Optional[int] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> int:
        inserted = session.execute(
            text(
                """
                INSERT INTO platform_audit_events
                    (tenant_account_id, service_id, domain_admin_token_id,
                     event_type, result, source_ip, user_agent, detail_json,
                     created_at)
                VALUES
                    (:tenant_account_id, :service_id, :domain_admin_token_id,
                     :event_type, :result, :source_ip, :user_agent, :detail_json,
                     UTC_TIMESTAMP())
                """
            ),
            {
                "tenant_account_id": tenant_account_id,
                "service_id": service_id,
                "domain_admin_token_id": domain_admin_token_id,
                "event_type": event_type,
                "result": result,
                "source_ip": source_ip,
                "user_agent": user_agent,
                "detail_json": json.dumps(detail) if detail is not None else None,
            },
        )
        return int(inserted.lastrowid)

    # --- domain_secrets ---

    def get_domain_secret(
        self, session: SessionLike, *, service_id: str, key: str
    ) -> Optional[dict[str, Any]]:
        """Одна строка domain_secrets (value_enc ещё зашифрован)."""
        row = session.execute(
            text(
                """
                SELECT service_id, `key`, value_enc, created_at, updated_at
                FROM domain_secrets
                WHERE service_id = :service_id AND `key` = :key
                """
            ),
            {"service_id": service_id, "key": key},
        ).mappings().first()
        return dict(row) if row else None

    def upsert_domain_secret(
        self,
        session: SessionLike,
        *,
        service_id: str,
        key: str,
        value_enc: str,
    ) -> None:
        """INSERT … ON DUPLICATE KEY UPDATE value_enc."""
        session.execute(
            text(
                """
                INSERT INTO domain_secrets (service_id, `key`, value_enc, created_at, updated_at)
                VALUES (:service_id, :key, :value_enc, UTC_TIMESTAMP(), UTC_TIMESTAMP())
                ON DUPLICATE KEY UPDATE
                    value_enc = VALUES(value_enc),
                    updated_at = UTC_TIMESTAMP()
                """
            ),
            {
                "service_id": service_id,
                "key": key,
                "value_enc": value_enc,
            },
        )

    def delete_domain_secret(
        self, session: SessionLike, *, service_id: str, key: str
    ) -> bool:
        result = session.execute(
            text(
                """
                DELETE FROM domain_secrets
                WHERE service_id = :service_id AND `key` = :key
                """
            ),
            {"service_id": service_id, "key": key},
        )
        return int(result.rowcount or 0) > 0

    def list_domain_secret_keys(
        self, session: SessionLike, *, service_id: str
    ) -> list[str]:
        """Имена ключей без значений."""
        rows = session.execute(
            text(
                """
                SELECT `key`
                FROM domain_secrets
                WHERE service_id = :service_id
                ORDER BY `key` ASC
                """
            ),
            {"service_id": service_id},
        ).mappings().all()
        return [str(r["key"]) for r in rows]

    # --- domain_services (boot) ---

    def list_active_domain_services(
        self, session: SessionLike, *, service_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Active domain_services; optional single-tenant filter for worker boot."""
        if service_id:
            rows = session.execute(
                text(
                    """
                    SELECT service_id, db_secret_ref,
                           db_graph_secret_ref, db_graph_write_secret_ref, status
                    FROM domain_services
                    WHERE status = 'active' AND service_id = :service_id
                    """
                ),
                {"service_id": service_id},
            ).mappings().all()
        else:
            rows = session.execute(
                text(
                    """
                    SELECT service_id, db_secret_ref,
                           db_graph_secret_ref, db_graph_write_secret_ref, status
                    FROM domain_services
                    WHERE status = 'active'
                    """
                )
            ).mappings().all()
        return [dict(r) for r in rows]

    # --- platform metrics (admin /v1/metrics) ---

    def collect_tenant_instance_queue_metrics(
        self, session: SessionLike, service_id: str
    ) -> dict[str, Any]:
        """Очередь instances одного tenant — для worker health в ЛК."""
        sid = str(service_id or "").strip()
        by_status = {
            str(r["status"]): int(r["n"])
            for r in session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM server_fsm_instances
                    WHERE service_id = :service_id
                    GROUP BY status
                    """
                ),
                {"service_id": sid},
            ).mappings()
        }
        oldest_pending = session.execute(
            text(
                """
                SELECT TIMESTAMPDIFF(SECOND, MIN(created_at), UTC_TIMESTAMP()) AS age_s
                FROM server_fsm_instances
                WHERE service_id = :service_id
                  AND status = 'PENDING'
                  AND (next_attempt_at IS NULL
                       OR next_attempt_at <= UTC_TIMESTAMP())
                """
            ),
            {"service_id": sid},
        ).scalar()
        return {
            "pending": int(by_status.get("PENDING") or 0),
            "processing": int(by_status.get("PROCESSING") or 0),
            "oldest_due_pending_age_seconds": int(oldest_pending)
            if oldest_pending is not None
            else None,
        }

    def collect_platform_queue_metrics(self, session: SessionLike) -> dict[str, Any]:
        """Агрегаты instances / outbox / reconcile / timers для ops-метрик."""
        instances = {
            str(r["status"]): int(r["n"])
            for r in session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM server_fsm_instances
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        oldest_pending = session.execute(
            text(
                """
                SELECT TIMESTAMPDIFF(SECOND, MIN(created_at), UTC_TIMESTAMP()) AS age_s
                FROM server_fsm_instances
                WHERE status = 'PENDING'
                  AND (next_attempt_at IS NULL
                       OR next_attempt_at <= UTC_TIMESTAMP())
                """
            )
        ).scalar()
        failed_1h = session.execute(
            text(
                """
                SELECT COUNT(*) FROM server_fsm_instances
                WHERE status = 'FAILED'
                  AND finished_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 1 HOUR)
                """
            )
        ).scalar()
        outbox = {
            str(r["status"]): int(r["n"])
            for r in session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM platform_outbox
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        oldest_outbox = session.execute(
            text(
                """
                SELECT TIMESTAMPDIFF(SECOND, MIN(created_at), UTC_TIMESTAMP()) AS age_s
                FROM platform_outbox
                WHERE status = 'PENDING'
                  AND next_attempt_at <= UTC_TIMESTAMP()
                """
            )
        ).scalar()
        reconcile = {
            str(r["status"]): int(r["n"])
            for r in session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS n
                    FROM platform_reconcile_queue
                    GROUP BY status
                    """
                )
            ).mappings()
        }
        timers_due = session.execute(
            text(
                """
                SELECT COUNT(*) FROM fsm_timers
                WHERE status = 'SCHEDULED'
                  AND fire_at <= UTC_TIMESTAMP()
                """
            )
        ).scalar()
        return {
            "instances": {
                "by_status": instances,
                "pending": int(instances.get("PENDING") or 0),
                "processing": int(instances.get("PROCESSING") or 0),
                "failed_1h": int(failed_1h or 0),
                "oldest_due_pending_age_seconds": int(oldest_pending or 0)
                if oldest_pending is not None
                else None,
            },
            "outbox": {
                "by_status": outbox,
                "pending": int(outbox.get("PENDING") or 0),
                "dead": int(outbox.get("DEAD") or 0),
                "oldest_due_pending_age_seconds": int(oldest_outbox or 0)
                if oldest_outbox is not None
                else None,
            },
            "reconcile": {
                "by_status": reconcile,
                "pending": int(reconcile.get("PENDING") or 0),
                "dead": int(reconcile.get("DEAD") or 0),
            },
            "timers": {"due_scheduled": int(timers_due or 0)},
        }


default_db_layer = FsmDbLayer()
