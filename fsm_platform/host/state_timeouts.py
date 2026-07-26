"""
Декларативный timeout состояния → runtime timer платформы.

Кто что владеет
---------------
Домен (граф fsm_states):
  Пишет ПОЛИТИКУ один раз в миграции/seed:
    timeout_seconds, timeout_event, timeout_owner
  Это не «таймер в базе домена», а описание ребра времени
  (как guard_name на transition — конфиг, не runtime).

Платформа (fsm_timers + worker):
  После успешного apply читает политику to_state.
  САМА создаёт/отменяет строку в platform.fsm_timers.
  Worker САМ claim due timer и САМ enqueue process.
  Инициатор wake-up и владелец runtime — platform.

Цепочка
-------
  transition apply → to_state
    → platform: INSERT fsm_timers (fire_at = now + timeout_seconds)
    → worker: fire_at due → insert_fsm_instance(process по timeout_event)
    → обычный FSM (guards/effects)

Без строк timeout_* в fsm_states платформа ничего не ставит.
Явный путь без графа: command возвращает timers[] → тот же fsm_timers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from fsm_platform.core.db_layer import SessionLike, default_db_layer
from fsm_platform.core.registry import default_process_registry
from fsm_platform.core.transition_repository import TransitionRepository
from fsm_platform.host import side_effects

logger = logging.getLogger(__name__)

_repo = TransitionRepository()


def state_timeout_idem_key(
    service_id: str, entity_type: str, entity_id: int
) -> str:
    return f"state_timeout:{service_id}:{entity_type}:{entity_id}"


def reschedule_after_transition(
    session_platform: SessionLike,
    session_domain: SessionLike,
    *,
    service_id: str,
    entity_type: str,
    entity_id: int,
    to_state: str,
    actor_id: Optional[int] = None,
    payload: Optional[dict[str, Any]] = None,
) -> Optional[int]:
    """
    Platform: сбросить предыдущий state-timeout сущности;
    если у to_state есть политика — поставить новый fsm_timers.
    """
    key = state_timeout_idem_key(service_id, entity_type, entity_id)
    default_db_layer.cancel_timer_by_idempotency_key(
        session_platform, service_id, key
    )

    meta = _repo.get_state_timeout(session_domain, entity_type, to_state)
    if meta is None:
        return None

    event_name = meta["timeout_event"]
    process = None
    for p in default_process_registry.list_for_service(service_id):
        if str(p.entity_type or "") != entity_type:
            continue
        if p.runtime_event_name == event_name:
            process = p
            break
    if process is None:
        logger.warning(
            "state timeout: no ProcessDef for event=%s entity_type=%s",
            event_name,
            entity_type,
        )
        return None

    fire_at = datetime.utcnow() + timedelta(seconds=int(meta["timeout_seconds"]))
    timer_payload = dict(payload or {})
    if actor_id is not None:
        timer_payload.setdefault("actor_id", actor_id)
        timer_payload.setdefault("executor_user_id", actor_id)

    timer_id = side_effects.schedule_timer(
        session_platform,
        service_id=service_id,
        entity_type=entity_type,
        entity_id=entity_id,
        process_name=process.process_name,
        fire_at=fire_at,
        payload=timer_payload,
        idempotency_key=key,
        owner=str(meta["timeout_owner"]),
    )
    logger.info(
        "platform scheduled state timeout entity=%s/%s state=%s event=%s in=%ss timer=%s",
        entity_type,
        entity_id,
        to_state,
        event_name,
        meta["timeout_seconds"],
        timer_id,
    )
    return timer_id
