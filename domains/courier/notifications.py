"""TG-уведомления о прогрессе заказа (platform.notify → outbox)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fsm_platform.host import side_effects

from domains.courier import db_layer

logger = logging.getLogger(__name__)

# to_state → audience → шаблон
_ORDER_PROGRESS_TEMPLATES: dict[str, dict[str, str]] = {
    "order_created": {
        "client": "Заказ №{order_id} успешно создан.",
    },
    "order_courier1_assigned": {
        "client": (
            "Заказ №{order_id} принял курьер {courier_name}. "
            "Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку."
        ),
    },
    "order_parcel_confirmed": {
        "client": (
            "Посылка по заказу №{order_id} сдана в постамат: "
            "{locker_address} (ячейка {cell_code})."
        ),
    },
    "order_picked_up_from_post1": {
        "client": (
            "Посылка по заказу №{order_id} забрана из постамата отправления "
            "и готовится к отправке."
        ),
    },
    "order_in_transit_to_post2": {
        "client": "Заказ №{order_id}: посылка в пути.",
        "recipient": "Вам отправление №{order_id}: посылка в пути к вам.",
    },
    "order_parcel_confirmed_post2": {
        "client": (
            "Заказ №{order_id}: посылка прибыла в постамат назначения "
            "({locker_address})."
        ),
        "recipient": (
            "Ваша посылка №{order_id} в постамате: "
            "{locker_address} (ячейка {cell_code})."
        ),
    },
    "order_courier2_assigned": {
        "recipient": (
            "Заказ №{order_id} принял курьер {courier_name} для доставки вам."
        ),
    },
    "order_courier2_parcel_delivered": {
        "recipient": (
            "Курьер доставил посылку по заказу №{order_id}. "
            "Ожидается подтверждение получения."
        ),
    },
    "order_completed": {
        "client": "Заказ №{order_id} успешно завершён.",
        "recipient": "Заказ №{order_id}: получение подтверждено. Спасибо!",
    },
}


def _platform_session(db: Any):
    if isinstance(db, dict):
        return db.get("platform")
    return None


def _cell_fields(session_domain, cell_id: Optional[int]) -> dict[str, str]:
    if not cell_id:
        return {"locker_address": "—", "cell_code": "—"}
    info = db_layer.get_cell_display(session_domain, int(cell_id))
    if not info:
        return {"locker_address": "—", "cell_code": "—"}
    return {
        "locker_address": str(info.get("locker_address") or "—"),
        "cell_code": str(info.get("cell_code") or "—"),
    }


def enqueue_order_progress_notifications(
    session_domain,
    db: Any,
    *,
    order_id: int,
    to_state: str,
    service_id: str = "svc_courier_01",
    instance_id: Optional[int] = None,
    courier_user_id: Optional[int] = None,
    platform_session=None,
) -> int:
    """
    Кладёт TG-сообщения в platform_outbox для client/recipient по to_state.
    Нужен users.telegram_chat_id (после deep-link /start из приложения).
    Без chat_id — skip. Возвращает число enqueued.
    """
    sp = platform_session or _platform_session(db)
    if sp is None:
        logger.debug("skip order notify: no platform session order_id=%s", order_id)
        return 0

    templates = _ORDER_PROGRESS_TEMPLATES.get(str(to_state) or "")
    if not templates:
        return 0

    order = db_layer.get_order(session_domain, int(order_id))
    if order is None:
        return 0

    courier_name = ""
    if courier_user_id:
        courier = db_layer.get_user(session_domain, int(courier_user_id))
        if courier:
            courier_name = str(courier.get("name") or "")

    status = str(to_state)
    if status in (
        "order_parcel_confirmed",
        "order_picked_up_from_post1",
        "order_courier1_assigned",
        "order_created",
    ):
        cell_id = order.get("source_cell_id")
    else:
        cell_id = order.get("dest_cell_id")
    cell = _cell_fields(session_domain, int(cell_id) if cell_id else None)

    audience_user = {
        "client": order.get("client_user_id"),
        "recipient": order.get("recipient_user_id"),
    }

    enqueued = 0
    for audience, template in templates.items():
        user_id = audience_user.get(audience)
        if not user_id:
            continue
        user = db_layer.get_user(session_domain, int(user_id))
        if user is None:
            continue
        chat_id = str(user.get("telegram_chat_id") or "").strip()
        if not chat_id:
            continue

        text = template.format(
            order_id=int(order_id),
            courier_name=courier_name or "курьер",
            locker_address=cell["locker_address"],
            cell_code=cell["cell_code"],
        )
        idem = f"tg:{order_id}:{to_state}:{audience}"
        if instance_id:
            idem = f"{idem}:i{instance_id}"
        try:
            side_effects.notify(
                sp,
                service_id=service_id,
                channel="telegram",
                destination=chat_id,
                event_type=f"order.progress.{to_state}",
                payload={
                    "text": text,
                    "order_id": int(order_id),
                    "to_state": to_state,
                    "audience": audience,
                    "user_id": int(user_id),
                },
                idempotency_key=idem,
            )
            enqueued += 1
        except Exception:
            logger.debug(
                "notify skip/dup order_id=%s state=%s audience=%s",
                order_id,
                to_state,
                audience,
                exc_info=True,
            )
    return enqueued
