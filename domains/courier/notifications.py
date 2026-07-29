"""TG-уведомления о прогрессе заказа — только сборка notify[] для ответа Contract API."""

from __future__ import annotations

import logging
from typing import Any, Optional

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
        "client": "Курьер забрал посылку №{order_id} из постамата отправления.",
    },
    "order_in_transit": {
        "client": "Заказ №{order_id} в пути.",
        "recipient": "Вам едет посылка №{order_id}.",
    },
    "order_courier2_assigned": {
        "recipient": (
            "Заказ №{order_id}: курьер {courier_name} назначен на доставку."
        ),
    },
    "order_courier2_parcel_delivered": {
        "recipient": (
            "Посылка №{order_id} доставлена в постамат: "
            "{locker_address} (ячейка {cell_code})."
        ),
    },
    "order_completed": {
        "client": "Заказ №{order_id} успешно завершён.",
        "recipient": "Заказ №{order_id}: получение подтверждено. Спасибо!",
    },
}


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


def build_order_progress_notifications(
    session_domain,
    *,
    order_id: int,
    to_state: str,
    instance_id: Optional[int] = None,
    courier_user_id: Optional[int] = None,
) -> list[dict[str, Any]]:
    """
    Собирает notify[] для TG (client/recipient) по to_state.
    Без chat_id — skip. Платформа применяет список из ответа effect/command.
    """
    templates = _ORDER_PROGRESS_TEMPLATES.get(str(to_state) or "")
    if not templates:
        return []

    order = db_layer.get_order(session_domain, int(order_id))
    if order is None:
        return []

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

    items: list[dict[str, Any]] = []
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
        items.append(
            {
                "channel": "telegram",
                "destination": chat_id,
                "event_type": f"order.progress.{to_state}",
                "payload": {
                    "text": text,
                    "order_id": int(order_id),
                    "to_state": to_state,
                    "audience": audience,
                    "user_id": int(user_id),
                },
                "idempotency_key": idem,
            }
        )
    return items
