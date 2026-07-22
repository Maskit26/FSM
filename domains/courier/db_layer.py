"""SQL домена courier. Сессию передаёт Request Runtime или worker."""

from __future__ import annotations

import hashlib
import math
import re
from datetime import datetime
from typing import Any, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


def _city_hint(address: str) -> str:
    """Достаёт город из начала адреса до первой запятой. Нужен для подбора постамата без геокодера."""
    return address.split(",")[0].strip()


def _haversine_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Считает расстояние между двумя точками в километрах. Используется для выбора ближайшего постамата."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def find_nearest_free_cell(
    session: Session,
    *,
    address: str,
    cell_size: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    exclude_cell_id: Optional[int] = None,
) -> Optional[dict[str, Any]]:
    """
    Ищет свободную ячейку нужного размера у ближайшего подходящего постамата.
    При lat/lng предпочитает гео-дистанцию; иначе матчит город и текст адреса.
    """
    city = _city_hint(address)
    rows = session.execute(
        text(
            """
            SELECT
                lc.id AS cell_id,
                lc.locker_id,
                lc.cell_code,
                lc.cell_type,
                l.locker_code,
                l.city,
                l.location_address,
                l.latitude,
                l.longitude
            FROM locker_cells lc
            JOIN lockers l ON l.id = lc.locker_id
            WHERE lc.cell_type = :cell_size
              AND lc.status = 'locker_free'
              AND (:exclude_cell_id IS NULL OR lc.id <> :exclude_cell_id)
              AND (
                    l.city = :city
                 OR l.location_address LIKE :city_like
                 OR :city = ''
              )
            FOR UPDATE
            """
        ),
        {
            "cell_size": cell_size,
            "exclude_cell_id": exclude_cell_id,
            "city": city,
            "city_like": f"%{city}%",
        },
    ).mappings().all()
    if not rows:
        return None

    addr_l = address.casefold()
    city_l = city.casefold()

    scored: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        item = dict(row)
        locker_city = str(item.get("city") or "")
        locker_addr = str(item.get("location_address") or "")
        score = 1_000_000.0

        use_geo = (
            lat is not None
            and lng is not None
            and item.get("latitude") is not None
            and item.get("longitude") is not None
        )
        if use_geo:
            score = _haversine_km(
                float(lat),
                float(lng),
                float(item["latitude"]),
                float(item["longitude"]),
            )
        else:
            if locker_city and locker_city.casefold() == city_l:
                score = 100.0
            elif city_l and city_l in locker_addr.casefold():
                score = 200.0
            elif locker_city and locker_city.casefold() in addr_l:
                score = 300.0
            else:
                score = 900.0

            tokens = [t for t in re.split(r"[\s,]+", addr_l) if len(t) > 3]
            hits = sum(1 for t in tokens if t in locker_addr.casefold())
            score -= min(hits, 20) * 2.0

        scored.append((score, item))

    scored.sort(key=lambda x: (x[0], int(x[1]["cell_id"])))
    return scored[0][1]


def reserve_and_bind_cells(
    session: Session,
    order_id: int,
    source_cell_id: int,
    dest_cell_id: int,
) -> None:
    """
    Резервирует две ячейки под заказ и пишет current_order_id.
    Обе ячейки должны быть свободны, иначе ошибка.
    """
    result = session.execute(
        text(
            """
            UPDATE locker_cells
            SET status = 'locker_reserved',
                current_order_id = :order_id,
                updated_at = UTC_TIMESTAMP()
            WHERE (id = :source_id OR id = :dest_id)
              AND status = 'locker_free'
            """
        ),
        {
            "order_id": order_id,
            "source_id": source_cell_id,
            "dest_id": dest_cell_id,
        },
    )
    if int(result.rowcount or 0) != 2:
        raise RuntimeError("failed to reserve both cells")


def insert_order(
    session: Session,
    *,
    description: str,
    client_user_id: int,
    recipient_user_id: Optional[int] = None,
    delivery_type: str = "courier",
    pickup_type: str = "courier",
    parcel_type: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    source_cell_id: Optional[int] = None,
    dest_cell_id: Optional[int] = None,
) -> int:
    """
    Вставляет строку заказа со статусом order_created.
    Возвращает id созданного заказа.
    """
    result = session.execute(
        text(
            """
            INSERT INTO orders
                (status, description, delivery_type, pickup_type, parcel_type,
                 from_address, to_address,
                 client_user_id, recipient_user_id,
                 source_cell_id, dest_cell_id,
                 created_at, updated_at)
            VALUES
                ('order_created', :description, :delivery_type, :pickup_type, :parcel_type,
                 :from_address, :to_address,
                 :client_user_id, :recipient_user_id,
                 :source_cell_id, :dest_cell_id,
                 UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        ),
        {
            "description": description,
            "delivery_type": delivery_type,
            "pickup_type": pickup_type,
            "parcel_type": parcel_type,
            "from_address": from_address,
            "to_address": to_address,
            "client_user_id": client_user_id,
            "recipient_user_id": recipient_user_id,
            "source_cell_id": source_cell_id,
            "dest_cell_id": dest_cell_id,
        },
    )
    return int(result.lastrowid)


def update_order_status(session: Session, order_id: int, status: str) -> None:
    """Обновляет бизнес-статус заказа в таблице orders. Нужен для синхронизации с FSM."""
    session.execute(
        text(
            """
            UPDATE orders
            SET status = :status, updated_at = UTC_TIMESTAMP()
            WHERE id = :id
            """
        ),
        {"id": order_id, "status": status},
    )


def get_order(session: Session, order_id: int) -> Optional[dict[str, Any]]:
    """Читает заказ по id. Возвращает dict или None, если не найден."""
    row = session.execute(
        text(
            """
            SELECT id, status, description, delivery_type, pickup_type,
                   parcel_type, from_address, to_address,
                   client_user_id, recipient_user_id,
                   source_cell_id, dest_cell_id,
                   created_at, updated_at
            FROM orders WHERE id = :id
            """
        ),
        {"id": order_id},
    ).mappings().first()
    return dict(row) if row else None


def list_orders_for_client(
    session: Session, client_user_id: int, limit: int = 20
) -> list[dict[str, Any]]:
    """Список заказов клиента (новые сверху). Ограничивается limit."""
    rows = session.execute(
        text(
            """
            SELECT id, status, description, delivery_type,
                   from_address, to_address, created_at
            FROM orders
            WHERE client_user_id = :uid
            ORDER BY id DESC
            LIMIT :lim
            """
        ),
        {"uid": client_user_id, "lim": limit},
    ).mappings().all()
    return [dict(r) for r in rows]


def create_stage_order(
    session: Session,
    order_id: int,
    leg: str,
    *,
    trip_id: Optional[int] = None,
    courier_user_id: Optional[int] = None,
) -> None:
    """
    Создаёт слот плеча в stage_orders (pickup или delivery).
    Пока courier_user_id пуст — заказ доступен на бирже этого плеча.
    """
    session.execute(
        text(
            """
            INSERT INTO stage_orders (trip_id, order_id, leg, courier_user_id)
            VALUES (:trip_id, :order_id, :leg, :courier_user_id)
            """
        ),
        {
            "trip_id": trip_id,
            "order_id": order_id,
            "leg": leg,
            "courier_user_id": courier_user_id,
        },
    )


def claim_stage_order(
    session: Session,
    order_id: int,
    leg: str,
    courier_user_id: int,
) -> bool:
    """
    Атомарно занимает свободный слот биржи за курьером.
    True только если строка была свободна и обновлена.
    """
    result = session.execute(
        text(
            """
            UPDATE stage_orders
            SET courier_user_id = :cid
            WHERE order_id = :oid
              AND leg = :leg
              AND courier_user_id IS NULL
            """
        ),
        {"cid": courier_user_id, "oid": order_id, "leg": leg},
    )
    return int(result.rowcount or 0) == 1


def is_stage_slot_free(session: Session, order_id: int, leg: str) -> bool:
    """Read-only: свободен ли слот stage_orders для плеча (courier_user_id IS NULL)."""
    row = session.execute(
        text(
            """
            SELECT courier_user_id
            FROM stage_orders
            WHERE order_id = :oid AND leg = :leg
            """
        ),
        {"oid": order_id, "leg": leg},
    ).fetchone()
    if row is None:
        return False
    return row[0] is None


def get_stage_courier(
    session: Session, order_id: int, leg: str
) -> Optional[int]:
    """Кто сейчас на слоте stage_orders для плеча. None если слота нет или пуст."""
    row = session.execute(
        text(
            """
            SELECT courier_user_id
            FROM stage_orders
            WHERE order_id = :oid AND leg = :leg
            """
        ),
        {"oid": order_id, "leg": leg},
    ).fetchone()
    if row is None or row[0] is None:
        return None
    return int(row[0])


def clear_stage_courier(
    session: Session,
    order_id: int,
    leg: str,
    *,
    expected_courier_id: Optional[int] = None,
) -> bool:
    """
    Обнуляет courier_user_id на плече.
    Если expected_courier_id задан — снимает только если слот занят им (атомарно).
    """
    if expected_courier_id is not None:
        result = session.execute(
            text(
                """
                UPDATE stage_orders
                SET courier_user_id = NULL
                WHERE order_id = :oid
                  AND leg = :leg
                  AND courier_user_id = :cid
                """
            ),
            {"oid": order_id, "leg": leg, "cid": int(expected_courier_id)},
        )
    else:
        result = session.execute(
            text(
                """
                UPDATE stage_orders
                SET courier_user_id = NULL
                WHERE order_id = :oid AND leg = :leg
                """
            ),
            {"oid": order_id, "leg": leg},
        )
    return int(result.rowcount or 0) == 1


def set_stage_courier(
    session: Session,
    order_id: int,
    leg: str,
    courier_user_id: int,
) -> None:
    """Принудительно пишет courier_user_id в слот плеча (после успешного FSM)."""
    session.execute(
        text(
            """
            UPDATE stage_orders
            SET courier_user_id = :cid
            WHERE order_id = :oid AND leg = :leg
            """
        ),
        {"cid": courier_user_id, "oid": order_id, "leg": leg},
    )


def get_locker_city_by_cell(session: Session, cell_id: int) -> Optional[str]:
    """Город постамата по id ячейки. Нужен для проверки, что курьер из того же города."""
    row = session.execute(
        text(
            """
            SELECT l.city
            FROM locker_cells lc
            JOIN lockers l ON l.id = lc.locker_id
            WHERE lc.id = :cell_id
            """
        ),
        {"cell_id": cell_id},
    ).fetchone()
    return str(row[0]) if row and row[0] else None


def get_user(session: Session, user_id: int) -> Optional[dict[str, Any]]:
    """Читает пользователя (роль, город и т.д.). Нужен для биржи и авторизации актёра."""
    row = session.execute(
        text(
            """
            SELECT id, name, role_name, city, phone
            FROM users WHERE id = :id
            """
        ),
        {"id": user_id},
    ).mappings().first()
    return dict(row) if row else None


def list_exchange_pickup(
    session: Session, courier_city: str
) -> list[dict[str, Any]]:
    """
    Заказы на бирже pickup в городе курьера (клиент → постамат А).
    Только свободные слоты stage_orders и pickup_type=courier.
    """
    rows = session.execute(
        text(
            """
            SELECT
                o.id AS order_id,
                o.status,
                o.description,
                o.parcel_type,
                o.from_address,
                o.to_address,
                o.pickup_type,
                o.delivery_type,
                o.created_at,
                l.location_address AS locker_address,
                l.city AS locker_city,
                lc.cell_code,
                lc.cell_type AS cell_size
            FROM orders o
            JOIN stage_orders so
                ON so.order_id = o.id AND so.leg = 'pickup'
            JOIN locker_cells lc ON lc.id = o.source_cell_id
            JOIN lockers l ON l.id = lc.locker_id
            WHERE o.status = 'order_created'
              AND o.pickup_type = 'courier'
              AND so.courier_user_id IS NULL
              AND l.city = :courier_city
            ORDER BY o.created_at ASC
            """
        ),
        {"courier_city": courier_city},
    ).mappings().all()
    out = []
    for r in rows:
        item = dict(r)
        item["leg"] = "pickup"
        out.append(item)
    return out


def list_exchange_delivery(
    session: Session, courier_city: str
) -> list[dict[str, Any]]:
    """
    Заказы на бирже delivery в городе курьера (постамат Б → получатель).
    Показываются после статуса order_parcel_confirmed_post2.
    """
    rows = session.execute(
        text(
            """
            SELECT
                o.id AS order_id,
                o.status,
                o.description,
                o.parcel_type,
                o.from_address,
                o.to_address,
                o.pickup_type,
                o.delivery_type,
                o.created_at,
                l.location_address AS locker_address,
                l.city AS locker_city,
                lc.cell_code,
                lc.cell_type AS cell_size
            FROM orders o
            JOIN stage_orders so
                ON so.order_id = o.id AND so.leg = 'delivery'
            JOIN locker_cells lc ON lc.id = o.dest_cell_id
            JOIN lockers l ON l.id = lc.locker_id
            WHERE o.status = 'order_parcel_confirmed_post2'
              AND o.delivery_type = 'courier'
              AND so.courier_user_id IS NULL
              AND l.city = :courier_city
            ORDER BY o.created_at ASC
            """
        ),
        {"courier_city": courier_city},
    ).mappings().all()
    out = []
    for r in rows:
        item = dict(r)
        item["leg"] = "delivery"
        out.append(item)
    return out


def list_courier_exchange(
    session: Session, courier_city: str
) -> dict[str, Any]:
    """
    Собирает биржу города: pickup + delivery в одном результате.
    Поле all удобно отдавать на фронт одним списком.
    """
    pickup = list_exchange_pickup(session, courier_city)
    delivery = list_exchange_delivery(session, courier_city)
    return {
        "pickup": pickup,
        "delivery": delivery,
        "all": pickup + delivery,
        "counts": {
            "pickup": len(pickup),
            "delivery": len(delivery),
            "total": len(pickup) + len(delivery),
        },
    }


# Терминальные статусы заказа → «архив» для курьера
_COURIER_ARCHIVE_STATUSES = frozenset(
    {
        "order_completed",
        "order_cancelled",
        "order_courier_failed",
        "order_reservation_expired",
        "order_courier1_cancelled",
        "order_courier2_cancelled",
    }
)


def _courier_order_bucket(status: str) -> str:
    return "archive" if status in _COURIER_ARCHIVE_STATUSES else "active"


def list_orders_for_courier(
    session: Session,
    courier_user_id: int,
    *,
    status_filter: str = "all",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Заказы, уже взятые курьером (stage_orders.courier_user_id).
    status_filter: active | archive | all — для вкладок на фронте.
    """
    rows = session.execute(
        text(
            """
            SELECT
                o.id AS order_id,
                o.status,
                o.description,
                o.parcel_type,
                o.from_address,
                o.to_address,
                o.pickup_type,
                o.delivery_type,
                o.source_cell_id,
                o.dest_cell_id,
                o.created_at,
                o.updated_at,
                so.leg
            FROM orders o
            JOIN stage_orders so ON so.order_id = o.id
            WHERE so.courier_user_id = :courier_id
            ORDER BY o.updated_at DESC, o.id DESC
            LIMIT :lim
            """
        ),
        {"courier_id": courier_user_id, "lim": limit},
    ).mappings().all()

    filt = (status_filter or "all").strip().lower()
    if filt not in ("active", "archive", "all"):
        raise ValueError("filter must be active|archive|all")

    out: list[dict[str, Any]] = []
    for r in rows:
        item = dict(r)
        status = str(item.get("status") or "")
        bucket = _courier_order_bucket(status)
        item["bucket"] = bucket
        if filt != "all" and bucket != filt:
            continue
        out.append(item)
    return out


def get_cell_status(session: Session, cell_id: int) -> Optional[str]:
    """Текущий status ячейки (locker_reserved / locker_opened / …)."""
    row = session.execute(
        text("SELECT status FROM locker_cells WHERE id = :id"),
        {"id": cell_id},
    ).fetchone()
    if row is None or row[0] is None:
        return None
    return str(row[0])


def open_locker_cell(
    session: Session,
    cell_id: int,
    *,
    order_id: Optional[int] = None,
) -> bool:
    """
    Атомарно: locker_reserved|locker_occupied → locker_opened.
    Если order_id задан — только ячейка этого заказа.
    """
    if order_id is not None:
        result = session.execute(
            text(
                """
                UPDATE locker_cells
                SET status = 'locker_opened',
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :cell_id
                  AND current_order_id = :order_id
                  AND status IN ('locker_reserved', 'locker_occupied')
                """
            ),
            {"cell_id": cell_id, "order_id": order_id},
        )
    else:
        result = session.execute(
            text(
                """
                UPDATE locker_cells
                SET status = 'locker_opened',
                    updated_at = UTC_TIMESTAMP()
                WHERE id = :cell_id
                  AND status IN ('locker_reserved', 'locker_occupied')
                """
            ),
            {"cell_id": cell_id},
        )
    return int(result.rowcount or 0) == 1


def validate_access_code(
    session: Session,
    order_id: int,
    leg: str,
    user_id: int,
    pin: str,
    cell_id: int,
) -> Tuple[bool, str]:
    """
    Проверка PIN из cell_access_tokens (как старый validate_access_code).
    Hash: SHA256(f\"{pin}{order_id}{cell_id}\").
    """
    row = session.execute(
        text(
            """
            SELECT id, pin_hash, status, expires_at, cell_id
            FROM cell_access_tokens
            WHERE order_id = :order_id
              AND leg = :leg
              AND actor_user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"order_id": order_id, "leg": leg, "user_id": user_id},
    ).fetchone()
    if not row:
        return False, "ACCESS_CODE_NOT_FOUND"

    token_id, stored_pin_hash, token_status, expires_at, token_cell_id = row
    if str(token_status) != "ACTIVE":
        return False, f"ACCESS_CODE_NOT_ACTIVE:{token_status}"

    if expires_at is not None and expires_at < datetime.utcnow():
        return False, "ACCESS_CODE_EXPIRED"

    if int(token_cell_id) != int(cell_id):
        return False, "ACCESS_CODE_WRONG_CELL"

    expected_hash = hashlib.sha256(
        f"{pin}{order_id}{cell_id}".encode()
    ).hexdigest()
    if expected_hash != stored_pin_hash:
        session.execute(
            text(
                """
                UPDATE cell_access_tokens
                SET failed_attempts = failed_attempts + 1
                WHERE id = :token_id
                """
            ),
            {"token_id": token_id},
        )
        return False, "ACCESS_CODE_INVALID"

    return True, ""
