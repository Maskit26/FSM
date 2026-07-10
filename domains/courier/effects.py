from __future__ import annotations

import logging
from typing import Any, Dict, List

from fsm_core.types import EffectResult

logger = logging.getLogger(__name__)

SERVICE_NAME = "courier"


def noop_effect(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    """Пустой effect: SQL transition уже выполнен, побочных действий нет."""
    return EffectResult(ok=True)


def release_orders_on_reservation_cancel(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    """После SQL-перехода отмены резерва — вернуть заказы в пул направления."""
    reservation_id = instance.get("entity_id")
    if reservation_id is None:
        return EffectResult(ok=False, error="MISSING_ENTITY_ID")

    released_count = db.release_orders_from_reservation(session, reservation_id)
    return EffectResult(
        ok=True,
        payload={"released_count": released_count},
    )


def finalize_order_creation(
    session: Any,
    db: Any,
    context: Dict[str, Any],
    instance: Dict[str, Any],
    params: Dict[str, Any],
) -> EffectResult:
    """
    После перехода request_received → request_fulfilled:
    ячейки + orders + stage_orders + link + core_outbox.
    """
    request_id = context.get("request_id") or instance.get("entity_id")
    if request_id is None:
        return EffectResult(ok=False, error="MISSING_ENTITY_ID")

    from_city = context.get("from_city") or context.get("client_city")
    to_city = context.get("to_city") or context.get("recipient_city")
    cell_size = context.get("cell_size")
    client_user_id = context.get("client_user_id")
    recipient_user_id = context.get("recipient_user_id")
    pickup_type = context.get("pickup_type")
    delivery_type = context.get("delivery_type")
    parcel_type = context.get("parcel_type")
    description = context.get("description")

    if not all([from_city, to_city, cell_size, client_user_id, recipient_user_id,
                pickup_type, delivery_type, parcel_type, description]):
        return EffectResult(ok=False, error="INVALID_CONTEXT")

    try:
        created = db.create_order_from_request(
            session,
            request_id=request_id,
            from_city=from_city,
            to_city=to_city,
            cell_size=cell_size,
            client_user_id=client_user_id,
            recipient_user_id=recipient_user_id,
            pickup_type=pickup_type,
            delivery_type=delivery_type,
            parcel_type=parcel_type,
            description=description,
        )
    except Exception as exc:
        error = str(exc)
        if "NO_FREE_CELLS" in error:
            return EffectResult(ok=False, error="NO_FREE_CELLS")
        logger.exception("finalize_order_creation failed request_id=%s", request_id)
        return EffectResult(ok=False, error=error)

    order_id = created["order_id"]
    src_cell_id = created["src_cell_id"]
    dst_cell_id = created["dst_cell_id"]

    outbox_ids: List[int] = []
    main_outbox_id = db.enqueue_core_outbox(
        session=session,
        service=SERVICE_NAME,
        event_type="create_main_order",
        payload={
            "request_id": request_id,
            "local_order_id": order_id,
            "src_cell_id": src_cell_id,
            "dst_cell_id": dst_cell_id,
            "from_city": from_city,
            "to_city": to_city,
            "client_user_id": client_user_id,
            "recipient_user_id": recipient_user_id,
            "parcel_type": parcel_type,
            "cell_size": cell_size,
            "pickup_type": pickup_type,
            "delivery_type": delivery_type,
            "description": description,
        },
    )
    outbox_ids.append(main_outbox_id)

    if pickup_type == "courier":
        outbox_ids.append(
            db.enqueue_core_outbox(
                session=session,
                service=SERVICE_NAME,
                event_type="create_suborder",
                payload={
                    "local_order_id": order_id,
                    "role": "courier1",
                    "depends_on_outbox_id": main_outbox_id,
                },
            )
        )

    if delivery_type == "courier":
        outbox_ids.append(
            db.enqueue_core_outbox(
                session=session,
                service=SERVICE_NAME,
                event_type="create_suborder",
                payload={
                    "local_order_id": order_id,
                    "role": "courier2",
                    "depends_on_outbox_id": main_outbox_id,
                },
            )
        )

    logger.info(
        "[ORDER] created request_id=%s order_id=%s cells=%s/%s outbox=%s",
        request_id,
        order_id,
        src_cell_id,
        dst_cell_id,
        outbox_ids,
    )
    return EffectResult(
        ok=True,
        payload={
            "request_id": request_id,
            "order_id": order_id,
            "src_cell_id": src_cell_id,
            "dst_cell_id": dst_cell_id,
            "core_outbox_ids": outbox_ids,
        },
    )
