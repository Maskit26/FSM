"""SQL домена courier. Сессию передаёт Request Runtime или worker."""

from __future__ import annotations

import hashlib
import math
import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


def _city_hint(address: str) -> str:
    """Достаёт город из начала адреса до первой запятой. Нужен для подбора постамата без геокодера."""
    return address.split(",")[0].strip()


def list_cell_types(session: Session) -> frozenset[str]:
    """Допустимые cell_type из ENUM locker_cells.cell_type (источник — схема БД)."""
    raw = session.execute(
        text(
            """
            SELECT COLUMN_TYPE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'locker_cells'
              AND COLUMN_NAME = 'cell_type'
            """
        )
    ).scalar()
    if not raw:
        return frozenset()
    # enum('S','M','L','P') → {S,M,L,P}
    inner = str(raw)
    if inner.lower().startswith("enum("):
        inner = inner[5:]
    if inner.endswith(")"):
        inner = inner[:-1]
    values = {
        part.strip().strip("'").strip('"').upper()
        for part in inner.split(",")
        if part.strip()
    }
    return frozenset(v for v in values if v)


def normalize_cell_size(session: Session, raw: Any) -> str:
    """Нормализует cell_size и сверяет со схемой БД. Иначе ValueError."""
    if raw is None or str(raw).strip() == "":
        raise ValueError("cell_size required")
    size = str(raw).strip().upper()
    allowed = list_cell_types(session)
    if not allowed:
        raise ValueError("cell_size catalog unavailable")
    if size not in allowed:
        raise ValueError(f"cell_size must be one of {sorted(allowed)}")
    return size


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


def reserve_cell_for_order(
    session: Session,
    cell_id: int,
    order_id: int,
) -> bool:
    """
    Атомарно: locker_free → locker_reserved + current_order_id.
    Возвращает True только если CAS успешен (ячейка была свободна).
    """
    result = session.execute(
        text(
            """
            UPDATE locker_cells
            SET status = 'locker_reserved',
                current_order_id = :order_id,
                updated_at = UTC_TIMESTAMP()
            WHERE id = :cell_id
              AND status = 'locker_free'
            """
        ),
        {"cell_id": cell_id, "order_id": order_id},
    )
    return int(result.rowcount or 0) == 1


def reserve_and_bind_cells(
    session: Session,
    order_id: int,
    source_cell_id: int,
    dest_cell_id: int,
) -> None:
    """
    Резервирует две ячейки под заказ (sync helper).
    Для create_order используйте FSM locker_reserve_cell.
    """
    ok_src = reserve_cell_for_order(session, source_cell_id, order_id)
    ok_dst = reserve_cell_for_order(session, dest_cell_id, order_id)
    if not (ok_src and ok_dst):
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


def get_stage_row(
    session: Session, order_id: int, leg: str
) -> Optional[dict[str, Any]]:
    """Строка stage_orders для плеча (courier / driver reserve / trip)."""
    row = session.execute(
        text(
            """
            SELECT order_id, leg, trip_id, direction_id, courier_user_id,
                   reservation_id, reserved_by_driver_id
            FROM stage_orders
            WHERE order_id = :oid AND leg = :leg
            """
        ),
        {"oid": order_id, "leg": leg},
    ).mappings().first()
    return dict(row) if row else None


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


def get_locker_id_by_cell(session: Session, cell_id: int) -> Optional[int]:
    """locker_id постамата по id ячейки."""
    row = session.execute(
        text("SELECT locker_id FROM locker_cells WHERE id = :cell_id"),
        {"cell_id": cell_id},
    ).fetchone()
    if row is None or row[0] is None:
        return None
    return int(row[0])


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


def set_cell_status(session: Session, cell_id: int, status: str) -> bool:
    """Пишет locker_cells.status = status (зеркало entity_fsm_state после companion)."""
    result = session.execute(
        text(
            """
            UPDATE locker_cells
            SET status = :status,
                updated_at = UTC_TIMESTAMP()
            WHERE id = :cell_id
            """
        ),
        {"cell_id": cell_id, "status": status},
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


def count_recent_access_code_requests(
    session: Session, order_id: int, leg: str, minutes: int = 15
) -> int:
    """Сколько токенов создано за последние minutes по order+leg."""
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    result = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM cell_access_tokens
            WHERE order_id = :order_id
              AND leg = :leg
              AND created_at > :cutoff
            """
        ),
        {"order_id": order_id, "leg": leg, "cutoff": cutoff},
    ).scalar()
    return int(result or 0)


def generate_and_store_access_token(
    session: Session,
    order_id: int,
    leg: str,
    cell_id: int,
    actor_user_id: int,
    *,
    expires_minutes: int = 15,
) -> tuple[str, int, datetime]:
    """
    Генерирует 6-значный PIN, пишет cell_access_tokens.
    pin_encrypted — plaintext для view (тест); сверка open_cell идёт по pin_hash.
    """
    session.execute(
        text(
            """
            UPDATE cell_access_tokens
            SET status = 'REVOKED'
            WHERE order_id = :order_id
              AND leg = :leg
              AND actor_user_id = :actor_user_id
              AND status = 'ACTIVE'
            """
        ),
        {
            "order_id": order_id,
            "leg": leg,
            "actor_user_id": actor_user_id,
        },
    )

    pin = f"{secrets.randbelow(900000) + 100000:06d}"
    pin_hash = hashlib.sha256(f"{pin}{order_id}{cell_id}".encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

    result = session.execute(
        text(
            """
            INSERT INTO cell_access_tokens (
                order_id, leg, cell_id, actor_user_id,
                pin_hash, pin_encrypted, expires_at
            ) VALUES (
                :order_id, :leg, :cell_id, :actor_user_id,
                :pin_hash, :pin_encrypted, :expires_at
            )
            """
        ),
        {
            "order_id": order_id,
            "leg": leg,
            "cell_id": cell_id,
            "actor_user_id": actor_user_id,
            "pin_hash": pin_hash,
            "pin_encrypted": pin,
            "expires_at": expires_at,
        },
    )
    token_id = int(result.lastrowid)
    return pin, token_id, expires_at


def get_access_token_pin(
    session: Session, order_id: int, leg: str, user_id: int
) -> Optional[str]:
    """Читает plaintext PIN активного неистёкшего токена (для view / теста)."""
    row = session.execute(
        text(
            """
            SELECT pin_encrypted, expires_at, status
            FROM cell_access_tokens
            WHERE order_id = :order_id
              AND leg = :leg
              AND actor_user_id = :user_id
              AND status = 'ACTIVE'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"order_id": order_id, "leg": leg, "user_id": user_id},
    ).fetchone()
    if not row:
        return None
    pin, expires_at, status = row
    if str(status) != "ACTIVE":
        return None
    if expires_at is not None and expires_at < datetime.utcnow():
        return None
    if pin is None or str(pin).strip() == "":
        return None
    return str(pin).strip()


def get_or_create_direction(
    session: Session,
    from_city: str,
    to_city: str,
    pickup_locker_id: int,
    delivery_locker_id: int,
) -> int:
    """Находит или создаёт directions по (cities + lockers)."""
    existing = session.execute(
        text(
            """
            SELECT id FROM directions
            WHERE from_city = :from_city
              AND to_city = :to_city
              AND pickup_locker_id = :pickup_locker_id
              AND delivery_locker_id = :delivery_locker_id
            """
        ),
        {
            "from_city": from_city,
            "to_city": to_city,
            "pickup_locker_id": pickup_locker_id,
            "delivery_locker_id": delivery_locker_id,
        },
    ).fetchone()
    if existing:
        return int(existing[0])

    session.execute(
        text(
            """
            INSERT INTO directions (
                from_city, to_city, pickup_locker_id, delivery_locker_id,
                orders_reserved, orders_available
            ) VALUES (
                :from_city, :to_city, :pickup_locker_id, :delivery_locker_id,
                0, 0
            )
            """
        ),
        {
            "from_city": from_city,
            "to_city": to_city,
            "pickup_locker_id": pickup_locker_id,
            "delivery_locker_id": delivery_locker_id,
        },
    )
    return int(session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one())


def recalculate_direction_counters(session: Session, direction_id: int) -> None:
    """Пересчёт orders_available / orders_reserved из stage_orders."""
    available = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT order_id)
            FROM stage_orders
            WHERE direction_id = :direction_id
              AND leg = 'pickup'
              AND reservation_id IS NULL
              AND trip_id IS NULL
            """
        ),
        {"direction_id": direction_id},
    ).scalar()
    reserved = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT order_id)
            FROM stage_orders
            WHERE direction_id = :direction_id
              AND leg = 'pickup'
              AND reservation_id IS NOT NULL
              AND trip_id IS NULL
            """
        ),
        {"direction_id": direction_id},
    ).scalar()
    session.execute(
        text(
            """
            UPDATE directions
            SET orders_available = :available,
                orders_reserved = :reserved
            WHERE id = :direction_id
            """
        ),
        {
            "available": int(available or 0),
            "reserved": int(reserved or 0),
            "direction_id": direction_id,
        },
    )


def assign_order_to_direction(
    session: Session,
    order_id: int,
    from_city: str,
    to_city: str,
    pickup_locker_id: int,
    delivery_locker_id: int,
) -> int:
    """
    get_or_create direction + stage_orders.direction_id на pickup/delivery.
    Возвращает direction_id.
    """
    direction_id = get_or_create_direction(
        session, from_city, to_city, pickup_locker_id, delivery_locker_id
    )
    session.execute(
        text(
            """
            UPDATE stage_orders
            SET direction_id = :direction_id
            WHERE order_id = :order_id
              AND leg IN ('pickup', 'delivery')
            """
        ),
        {"direction_id": direction_id, "order_id": order_id},
    )
    recalculate_direction_counters(session, direction_id)
    return direction_id


def bind_order_to_direction(session: Session, order_id: int) -> tuple[int, str]:
    """
    Как старый bind_order_to_trip: после order_parcel_confirmed
    привязать заказ к directions (создать если нет).
    Returns (direction_id, error). error='' при успехе.
    """
    order = get_order(session, order_id)
    if order is None:
        return 0, "ORDER_NOT_FOUND"
    if str(order.get("status") or "") != "order_parcel_confirmed":
        return 0, "ORDER_NOT_CONFIRMED"

    source_cell_id = order.get("source_cell_id")
    dest_cell_id = order.get("dest_cell_id")
    if not source_cell_id or not dest_cell_id:
        return 0, "CELLS_MISSING"

    pickup_locker_id = get_locker_id_by_cell(session, int(source_cell_id))
    delivery_locker_id = get_locker_id_by_cell(session, int(dest_cell_id))
    from_city = get_locker_city_by_cell(session, int(source_cell_id))
    to_city = get_locker_city_by_cell(session, int(dest_cell_id))
    if not pickup_locker_id or not delivery_locker_id:
        return 0, "LOCKER_MISSING"
    if not from_city or not to_city:
        return 0, "CITY_MISSING"

    direction_id = assign_order_to_direction(
        session,
        order_id,
        from_city,
        to_city,
        pickup_locker_id,
        delivery_locker_id,
    )
    return direction_id, ""


def get_direction(session: Session, direction_id: int) -> Optional[dict[str, Any]]:
    """Читает направление по id."""
    row = session.execute(
        text(
            """
            SELECT id, from_city, to_city, pickup_locker_id, delivery_locker_id,
                   orders_available, orders_reserved
            FROM directions
            WHERE id = :id
            """
        ),
        {"id": direction_id},
    ).mappings().first()
    return dict(row) if row else None


def list_directions_for_driver_exchange(
    session: Session, city: str
) -> list[dict[str, Any]]:
    """
    Биржа водителя: коридоры (from_city → to_city) с суммой available
    по всем парам постаматов. Пары — в pairs[] для прозрачности.
    """
    corridor_rows = session.execute(
        text(
            """
            SELECT
                d.from_city,
                d.to_city,
                COUNT(DISTINCT so.order_id) AS orders_available
            FROM directions d
            JOIN stage_orders so
              ON so.direction_id = d.id AND so.leg = 'pickup'
            JOIN orders o ON o.id = so.order_id
            WHERE d.from_city = :city
              AND so.reserved_by_driver_id IS NULL
              AND so.trip_id IS NULL
              AND o.status IN ('order_parcel_confirmed', 'order_parcel_submitted')
            GROUP BY d.from_city, d.to_city
            HAVING COUNT(DISTINCT so.order_id) > 0
            ORDER BY d.from_city ASC, d.to_city ASC
            """
        ),
        {"city": city},
    ).mappings().all()

    pair_rows = session.execute(
        text(
            """
            SELECT
                d.id AS direction_id,
                d.from_city,
                d.to_city,
                d.pickup_locker_id,
                d.delivery_locker_id,
                COUNT(DISTINCT so.order_id) AS orders_available
            FROM directions d
            JOIN stage_orders so
              ON so.direction_id = d.id AND so.leg = 'pickup'
            JOIN orders o ON o.id = so.order_id
            WHERE d.from_city = :city
              AND so.reserved_by_driver_id IS NULL
              AND so.trip_id IS NULL
              AND o.status IN ('order_parcel_confirmed', 'order_parcel_submitted')
            GROUP BY
                d.id, d.from_city, d.to_city,
                d.pickup_locker_id, d.delivery_locker_id
            HAVING COUNT(DISTINCT so.order_id) > 0
            ORDER BY d.id ASC
            """
        ),
        {"city": city},
    ).mappings().all()

    pairs_by_corridor: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in pair_rows:
        key = (str(row["from_city"]), str(row["to_city"]))
        pairs_by_corridor.setdefault(key, []).append(
            {
                "direction_id": int(row["direction_id"]),
                "pickup_locker_id": int(row["pickup_locker_id"]),
                "delivery_locker_id": int(row["delivery_locker_id"]),
                "orders_available": int(row["orders_available"] or 0),
            }
        )

    out: list[dict[str, Any]] = []
    for row in corridor_rows:
        from_city = str(row["from_city"])
        to_city = str(row["to_city"])
        pairs = pairs_by_corridor.get((from_city, to_city), [])
        reserved = count_reserved_orders_on_corridor(session, from_city, to_city)
        out.append(
            {
                "from_city": from_city,
                "to_city": to_city,
                "orders_available": int(row["orders_available"] or 0),
                "orders_reserved": reserved,
                "pairs": pairs,
            }
        )
    return out


def count_available_orders_on_corridor(
    session: Session, from_city: str, to_city: str
) -> int:
    """Свободные заказы на коридоре (все пары постаматов)."""
    n = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT so.order_id)
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            JOIN directions d ON d.id = so.direction_id
            WHERE d.from_city = :from_city
              AND d.to_city = :to_city
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id IS NULL
              AND so.trip_id IS NULL
              AND o.status IN ('order_parcel_confirmed', 'order_parcel_submitted')
            """
        ),
        {"from_city": from_city, "to_city": to_city},
    ).scalar()
    return int(n or 0)


def count_reserved_orders_on_corridor(
    session: Session, from_city: str, to_city: str
) -> int:
    """Заказы коридора, уже в резерве (ещё без trip)."""
    n = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT so.order_id)
            FROM stage_orders so
            JOIN directions d ON d.id = so.direction_id
            WHERE d.from_city = :from_city
              AND d.to_city = :to_city
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id IS NOT NULL
              AND so.trip_id IS NULL
            """
        ),
        {"from_city": from_city, "to_city": to_city},
    ).scalar()
    return int(n or 0)


def count_active_driver_slots_on_corridor(
    session: Session, from_city: str, to_city: str, driver_user_id: int
) -> int:
    """Число active|loading резервов водителя на коридоре."""
    n = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM driver_reservations dr
            JOIN directions d ON d.id = dr.direction_id
            WHERE dr.driver_user_id = :driver_user_id
              AND d.from_city = :from_city
              AND d.to_city = :to_city
              AND dr.status IN ('reservation_active', 'reservation_loading')
            """
        ),
        {
            "driver_user_id": driver_user_id,
            "from_city": from_city,
            "to_city": to_city,
        },
    ).scalar()
    return int(n or 0)


def list_pickup_stops_for_reservation(
    session: Session, reservation_id: int
) -> list[dict[str, Any]]:
    """Группировка заказов резерва по pickup-постамату (для UI погрузки)."""
    rows = session.execute(
        text(
            """
            SELECT
                l.id AS locker_id,
                l.locker_code,
                l.city,
                l.location_address,
                so.order_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            JOIN locker_cells lc ON lc.id = o.source_cell_id
            JOIN lockers l ON l.id = lc.locker_id
            WHERE so.reservation_id = :reservation_id
              AND so.leg = 'pickup'
            ORDER BY l.id ASC, so.order_id ASC
            """
        ),
        {"reservation_id": reservation_id},
    ).mappings().all()

    by_locker: dict[int, dict[str, Any]] = {}
    for row in rows:
        lid = int(row["locker_id"])
        stop = by_locker.get(lid)
        if stop is None:
            stop = {
                "locker_id": lid,
                "locker_code": row.get("locker_code"),
                "city": row.get("city"),
                "location_address": row.get("location_address"),
                "order_ids": [],
            }
            by_locker[lid] = stop
        stop["order_ids"].append(int(row["order_id"]))
    return list(by_locker.values())


def reserve_orders_for_direction(
    session: Session,
    direction_id: int,
    driver_user_id: int,
    capacity: int,
) -> tuple[int, int, datetime, list[int]]:
    """Compat: direction_id → коридор (from_city/to_city) → reserve."""
    direction = get_direction(session, direction_id)
    if direction is None:
        raise ValueError("DIRECTION_NOT_FOUND")
    return reserve_orders_for_corridor(
        session,
        str(direction["from_city"]),
        str(direction["to_city"]),
        driver_user_id,
        capacity,
    )


def reserve_orders_for_corridor(
    session: Session,
    from_city: str,
    to_city: str,
    driver_user_id: int,
    capacity: int,
) -> tuple[int, int, datetime, list[int]]:
    """
    Резерв до capacity заказов по коридору (все пары постаматов).
    Returns (reservation_id, reserved_count, expires_at, order_ids).
    reservation.direction_id = anchor (direction первого взятого заказа).
    """
    if capacity <= 0:
        raise ValueError("INVALID_CAPACITY")
    from_city = str(from_city or "").strip()
    to_city = str(to_city or "").strip()
    if not from_city or not to_city:
        raise ValueError("CITY_REQUIRED")

    if count_active_driver_slots_on_corridor(
        session, from_city, to_city, driver_user_id
    ) >= 3:
        raise ValueError("LIMIT_EXCEEDED")

    if count_available_orders_on_corridor(session, from_city, to_city) <= 0:
        raise ValueError("NO_AVAILABLE_ORDERS")

    order_rows = session.execute(
        text(
            f"""
            SELECT so.order_id, so.direction_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            JOIN directions d ON d.id = so.direction_id
            WHERE d.from_city = :from_city
              AND d.to_city = :to_city
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id IS NULL
              AND so.trip_id IS NULL
              AND o.status IN ('order_parcel_confirmed', 'order_parcel_submitted')
            ORDER BY so.order_id ASC
            LIMIT {int(capacity)}
            FOR UPDATE
            """
        ),
        {"from_city": from_city, "to_city": to_city},
    ).fetchall()
    if not order_rows:
        raise ValueError("RESERVATION_FAILED")

    order_ids = [int(r[0]) for r in order_rows]
    anchor_direction_id = int(order_rows[0][1])
    affected_direction_ids = sorted({int(r[1]) for r in order_rows})
    reserved_count = len(order_ids)

    expires_at = datetime.utcnow() + timedelta(hours=1)
    session.execute(
        text(
            """
            INSERT INTO driver_reservations (
                driver_user_id, direction_id, reserved_count,
                requested_count, expires_at, status
            ) VALUES (
                :driver_user_id, :direction_id, :reserved_count,
                :requested_count, :expires_at, 'reservation_active'
            )
            """
        ),
        {
            "driver_user_id": driver_user_id,
            "direction_id": anchor_direction_id,
            "reserved_count": reserved_count,
            "requested_count": capacity,
            "expires_at": expires_at,
        },
    )
    reservation_id = int(session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one())

    placeholders = ", ".join(f":order_{i}" for i in range(len(order_ids)))
    params: dict[str, Any] = {
        f"order_{i}": oid for i, oid in enumerate(order_ids)
    }
    params["driver_user_id"] = driver_user_id
    params["reservation_id"] = reservation_id

    session.execute(
        text(
            f"""
            UPDATE stage_orders
            SET reserved_by_driver_id = :driver_user_id,
                reservation_id = :reservation_id
            WHERE order_id IN ({placeholders})
              AND leg IN ('pickup', 'delivery')
            """
        ),
        params,
    )
    for did in affected_direction_ids:
        recalculate_direction_counters(session, did)
    return reservation_id, reserved_count, expires_at, order_ids


def get_driver_reservation(
    session: Session, reservation_id: int
) -> Optional[dict[str, Any]]:
    row = session.execute(
        text(
            """
            SELECT id, driver_user_id, direction_id, reserved_count, requested_count,
                   reserved_at, expires_at, status
            FROM driver_reservations
            WHERE id = :id
            """
        ),
        {"id": reservation_id},
    ).mappings().first()
    return dict(row) if row else None


def start_driver_reservation_loading(
    session: Session, reservation_id: int, driver_user_id: int
) -> bool:
    """reservation_active → reservation_loading (sync, без call_fsm_action)."""
    result = session.execute(
        text(
            """
            UPDATE driver_reservations
            SET status = 'reservation_loading'
            WHERE id = :id
              AND driver_user_id = :driver_user_id
              AND status = 'reservation_active'
            """
        ),
        {"id": reservation_id, "driver_user_id": driver_user_id},
    )
    return int(result.rowcount or 0) == 1


def set_reservation_status(
    session: Session, reservation_id: int, status: str
) -> bool:
    """Пишет driver_reservations.status (зеркало entity_fsm_state)."""
    result = session.execute(
        text(
            """
            UPDATE driver_reservations
            SET status = :status
            WHERE id = :id
            """
        ),
        {"id": reservation_id, "status": status},
    )
    return int(result.rowcount or 0) == 1


def get_driver_loading_reservations(
    session: Session, direction_id: int, driver_user_id: int
) -> list[int]:
    """Compat: direction_id → коридор → резервы водителя."""
    direction = get_direction(session, direction_id)
    if direction is None:
        return []
    return get_driver_loading_reservations_for_corridor(
        session,
        str(direction["from_city"]),
        str(direction["to_city"]),
        driver_user_id,
    )


def get_driver_loading_reservations_for_corridor(
    session: Session, from_city: str, to_city: str, driver_user_id: int
) -> list[int]:
    """Активные резервы водителя на коридоре (active|loading)."""
    rows = session.execute(
        text(
            """
            SELECT dr.id
            FROM driver_reservations dr
            JOIN directions d ON d.id = dr.direction_id
            WHERE dr.driver_user_id = :driver_user_id
              AND d.from_city = :from_city
              AND d.to_city = :to_city
              AND dr.status IN ('reservation_active', 'reservation_loading')
            ORDER BY dr.id ASC
            """
        ),
        {
            "driver_user_id": driver_user_id,
            "from_city": from_city,
            "to_city": to_city,
        },
    ).fetchall()
    return [int(r[0]) for r in rows]


def list_open_cells_for_driver_direction(
    session: Session, direction_id: int, driver_user_id: int
) -> list[int]:
    """Ячейки pickup-заказов водителя в статусе locker_opened."""
    rows = session.execute(
        text(
            """
            SELECT DISTINCT o.source_cell_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            JOIN locker_cells lc ON lc.id = o.source_cell_id
            WHERE so.direction_id = :direction_id
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id = :driver_user_id
              AND so.trip_id IS NULL
              AND lc.status = 'locker_opened'
            """
        ),
        {"direction_id": direction_id, "driver_user_id": driver_user_id},
    ).fetchall()
    return [int(r[0]) for r in rows if r[0] is not None]


def get_picked_orders_by_driver_and_direction(
    session: Session, direction_id: int, driver_user_id: int
) -> list[int]:
    """Заказы, которые водитель забрал (status after close pickup)."""
    rows = session.execute(
        text(
            """
            SELECT DISTINCT so.order_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            WHERE so.direction_id = :direction_id
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id = :driver_user_id
              AND so.trip_id IS NULL
              AND o.status = 'order_picked_up_from_post1'
            """
        ),
        {"direction_id": direction_id, "driver_user_id": driver_user_id},
    ).fetchall()
    return [int(r[0]) for r in rows]


def get_picked_orders_by_reservations(
    session: Session, reservation_ids: list[int]
) -> list[int]:
    """Picked-заказы только из указанных резервов (loading-слоты)."""
    if not reservation_ids:
        return []
    placeholders = ", ".join(f":rid_{i}" for i in range(len(reservation_ids)))
    params: dict[str, Any] = {
        f"rid_{i}": rid for i, rid in enumerate(reservation_ids)
    }
    rows = session.execute(
        text(
            f"""
            SELECT DISTINCT so.order_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            WHERE so.reservation_id IN ({placeholders})
              AND so.leg = 'pickup'
              AND so.trip_id IS NULL
              AND o.status = 'order_picked_up_from_post1'
            ORDER BY so.order_id ASC
            """
        ),
        params,
    ).fetchall()
    return [int(r[0]) for r in rows]


def list_open_cells_for_reservations(
    session: Session, reservation_ids: list[int]
) -> list[int]:
    """Открытые ячейки только по заказам указанных резервов."""
    if not reservation_ids:
        return []
    placeholders = ", ".join(f":rid_{i}" for i in range(len(reservation_ids)))
    params: dict[str, Any] = {
        f"rid_{i}": rid for i, rid in enumerate(reservation_ids)
    }
    rows = session.execute(
        text(
            f"""
            SELECT DISTINCT o.source_cell_id
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            JOIN locker_cells lc ON lc.id = o.source_cell_id
            WHERE so.reservation_id IN ({placeholders})
              AND so.leg = 'pickup'
              AND so.trip_id IS NULL
              AND lc.status = 'locker_opened'
            """
        ),
        params,
    ).fetchall()
    return [int(r[0]) for r in rows if r[0] is not None]


def release_unpicked_orders_by_reservations(
    session: Session,
    reservation_ids: list[int],
    picked_order_ids: list[int],
) -> int:
    """Снять резерв с незабранных заказов только в указанных слотах."""
    if not reservation_ids:
        return 0
    placeholders = ", ".join(f":rid_{i}" for i in range(len(reservation_ids)))
    params: dict[str, Any] = {
        f"rid_{i}": rid for i, rid in enumerate(reservation_ids)
    }
    reserved = session.execute(
        text(
            f"""
            SELECT DISTINCT so.order_id
            FROM stage_orders so
            WHERE so.reservation_id IN ({placeholders})
              AND so.leg = 'pickup'
              AND so.trip_id IS NULL
            """
        ),
        params,
    ).fetchall()
    reserved_ids = [int(r[0]) for r in reserved]
    picked = set(int(x) for x in picked_order_ids)
    to_release = [oid for oid in reserved_ids if oid not in picked]
    if not to_release:
        return 0

    oid_ph = ", ".join(f":oid_{i}" for i in range(len(to_release)))
    release_params: dict[str, Any] = {
        f"oid_{i}": oid for i, oid in enumerate(to_release)
    }
    result = session.execute(
        text(
            f"""
            UPDATE stage_orders
            SET reserved_by_driver_id = NULL,
                reservation_id = NULL
            WHERE order_id IN ({oid_ph})
              AND leg IN ('pickup', 'delivery')
            """
        ),
        release_params,
    )
    # counters: directions of released pickup rows
    dir_rows = session.execute(
        text(
            f"""
            SELECT DISTINCT direction_id
            FROM stage_orders
            WHERE order_id IN ({oid_ph})
              AND leg = 'pickup'
              AND direction_id IS NOT NULL
            """
        ),
        release_params,
    ).fetchall()
    for row in dir_rows:
        recalculate_direction_counters(session, int(row[0]))
    return int(result.rowcount or 0)


def release_unpicked_orders_by_driver_and_direction(
    session: Session,
    direction_id: int,
    driver_user_id: int,
    picked_order_ids: list[int],
) -> int:
    """Снять резерв с незабранных заказов, вернуть в пул направления."""
    reserved = session.execute(
        text(
            """
            SELECT DISTINCT so.order_id
            FROM stage_orders so
            WHERE so.direction_id = :direction_id
              AND so.reserved_by_driver_id = :driver_user_id
              AND so.leg = 'pickup'
              AND so.trip_id IS NULL
            """
        ),
        {"direction_id": direction_id, "driver_user_id": driver_user_id},
    ).fetchall()
    reserved_ids = [int(r[0]) for r in reserved]
    picked = set(int(x) for x in picked_order_ids)
    to_release = [oid for oid in reserved_ids if oid not in picked]
    if not to_release:
        return 0

    placeholders = ", ".join(f":oid_{i}" for i in range(len(to_release)))
    params: dict[str, Any] = {f"oid_{i}": oid for i, oid in enumerate(to_release)}
    params["direction_id"] = direction_id
    params["driver_user_id"] = driver_user_id
    result = session.execute(
        text(
            f"""
            UPDATE stage_orders
            SET reserved_by_driver_id = NULL,
                reservation_id = NULL
            WHERE direction_id = :direction_id
              AND reserved_by_driver_id = :driver_user_id
              AND order_id IN ({placeholders})
              AND leg IN ('pickup', 'delivery')
            """
        ),
        params,
    )
    recalculate_direction_counters(session, direction_id)
    return int(result.rowcount or 0)


def complete_driver_reservations_loading(
    session: Session, reservation_ids: list[int], driver_user_id: int
) -> int:
    """reservation_loading|active → reservation_completed для списка резервов."""
    if not reservation_ids:
        return 0
    placeholders = ", ".join(f":rid_{i}" for i in range(len(reservation_ids)))
    params: dict[str, Any] = {
        f"rid_{i}": rid for i, rid in enumerate(reservation_ids)
    }
    params["driver_user_id"] = driver_user_id
    result = session.execute(
        text(
            f"""
            UPDATE driver_reservations
            SET status = 'reservation_completed'
            WHERE id IN ({placeholders})
              AND driver_user_id = :driver_user_id
              AND status IN ('reservation_active', 'reservation_loading')
            """
        ),
        params,
    )
    return int(result.rowcount or 0)


def list_orders_by_reservation(
    session: Session, reservation_id: int
) -> list[dict[str, Any]]:
    """Заказы резерва (pickup stage) с текущим orders.status."""
    rows = session.execute(
        text(
            """
            SELECT DISTINCT o.id AS order_id, o.status
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            WHERE so.reservation_id = :reservation_id
              AND so.leg = 'pickup'
            ORDER BY o.id ASC
            """
        ),
        {"reservation_id": reservation_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def validate_reservation_for_cancellation(
    session: Session, reservation_id: int
) -> tuple[bool, list[int], str]:
    """
    Можно отменить, если резерв active|loading и все заказы
    ещё order_parcel_confirmed (водитель ничего не забрал).
    Returns (ok, blocked_order_ids, error_code).
    """
    reservation = get_driver_reservation(session, reservation_id)
    if reservation is None:
        return False, [], "RESERVATION_NOT_FOUND"
    status = str(reservation.get("status") or "")
    if status not in ("reservation_active", "reservation_loading"):
        return False, [], f"INVALID_RESERVATION_STATUS:{status}"

    orders = list_orders_by_reservation(session, reservation_id)
    if not orders:
        return False, [], "NO_ORDERS_IN_RESERVATION"

    blocked = [
        int(o["order_id"])
        for o in orders
        if str(o.get("status") or "") != "order_parcel_confirmed"
    ]
    if blocked:
        return False, blocked, f"ORDERS_NOT_CONFIRMED:{blocked}"
    return True, [], ""


def release_orders_from_reservation(session: Session, reservation_id: int) -> int:
    """
    Снять резерв с заказов: вернуть в пул направления
    (reserved_by_driver_id / reservation_id → NULL на pickup+delivery).
    Статус orders не меняется (остаётся order_parcel_confirmed).
    """
    reservation = get_driver_reservation(session, reservation_id)
    if reservation is None:
        raise ValueError("RESERVATION_NOT_FOUND")

    count = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT order_id)
            FROM stage_orders
            WHERE reservation_id = :reservation_id
              AND leg = 'pickup'
            """
        ),
        {"reservation_id": reservation_id},
    ).scalar()
    released = int(count or 0)
    if released == 0:
        return 0

    affected = session.execute(
        text(
            """
            SELECT DISTINCT direction_id
            FROM stage_orders
            WHERE reservation_id = :reservation_id
              AND direction_id IS NOT NULL
            """
        ),
        {"reservation_id": reservation_id},
    ).fetchall()

    session.execute(
        text(
            """
            UPDATE stage_orders
            SET reserved_by_driver_id = NULL,
                reservation_id = NULL
            WHERE reservation_id = :reservation_id
              AND leg IN ('pickup', 'delivery')
            """
        ),
        {"reservation_id": reservation_id},
    )
    for row in affected:
        recalculate_direction_counters(session, int(row[0]))
    return released


def create_trip_with_orders(
    session: Session,
    *,
    direction_id: int,
    driver_user_id: int,
    order_ids: list[int],
    from_city: Optional[str] = None,
    to_city: Optional[str] = None,
) -> int:
    """
    Создаёт trip (status=trip_assigned) и пишет trip_id в stage_orders
    для переданных заказов (pickup+delivery).
    Коридор: from_city/to_city; lockers — из первого заказа (multi-stop UI отдельно).
    """
    if not order_ids:
        raise ValueError("NO_ORDERS_FOR_TRIP")

    direction = get_direction(session, direction_id)
    if direction is None and (not from_city or not to_city):
        raise ValueError("DIRECTION_NOT_FOUND")

    trip_from = str(from_city or (direction or {}).get("from_city") or "").strip()
    trip_to = str(to_city or (direction or {}).get("to_city") or "").strip()
    if not trip_from or not trip_to:
        raise ValueError("CITY_REQUIRED")

    first = get_order(session, int(order_ids[0]))
    if first is None:
        raise ValueError("ORDER_NOT_FOUND")
    pickup_locker_id = get_locker_id_by_cell(session, int(first["source_cell_id"]))
    delivery_locker_id = get_locker_id_by_cell(session, int(first["dest_cell_id"]))
    if not pickup_locker_id or not delivery_locker_id:
        raise ValueError("LOCKER_MISSING")

    session.execute(
        text(
            """
            INSERT INTO trips (
                driver_user_id, from_city, to_city,
                pickup_locker_id, delivery_locker_id,
                status, active, created_at
            ) VALUES (
                :driver_user_id, :from_city, :to_city,
                :pickup_locker_id, :delivery_locker_id,
                'trip_assigned', 1, UTC_TIMESTAMP()
            )
            """
        ),
        {
            "driver_user_id": driver_user_id,
            "from_city": trip_from,
            "to_city": trip_to,
            "pickup_locker_id": pickup_locker_id,
            "delivery_locker_id": delivery_locker_id,
        },
    )
    trip_id = int(session.execute(text("SELECT LAST_INSERT_ID()")).scalar_one())

    placeholders = ", ".join(f":oid_{i}" for i in range(len(order_ids)))
    params: dict[str, Any] = {f"oid_{i}": oid for i, oid in enumerate(order_ids)}
    params["trip_id"] = trip_id
    session.execute(
        text(
            f"""
            UPDATE stage_orders
            SET trip_id = :trip_id
            WHERE order_id IN ({placeholders})
              AND leg IN ('pickup', 'delivery')
            """
        ),
        params,
    )

    affected = session.execute(
        text(
            f"""
            SELECT DISTINCT direction_id
            FROM stage_orders
            WHERE order_id IN ({placeholders})
              AND direction_id IS NOT NULL
            """
        ),
        {f"oid_{i}": oid for i, oid in enumerate(order_ids)},
    ).fetchall()
    for row in affected:
        recalculate_direction_counters(session, int(row[0]))
    return trip_id


def get_trip(session: Session, trip_id: int) -> Optional[dict[str, Any]]:
    row = session.execute(
        text(
            """
            SELECT id, driver_user_id, from_city, to_city,
                   pickup_locker_id, delivery_locker_id,
                   status, description, active, created_at
            FROM trips
            WHERE id = :id
            """
        ),
        {"id": trip_id},
    ).mappings().first()
    return dict(row) if row else None


def set_trip_status(session: Session, trip_id: int, status: str) -> bool:
    result = session.execute(
        text(
            """
            UPDATE trips
            SET status = :status
            WHERE id = :id
            """
        ),
        {"id": trip_id, "status": status},
    )
    return int(result.rowcount or 0) == 1


def list_trip_order_ids(session: Session, trip_id: int) -> list[int]:
    rows = session.execute(
        text(
            """
            SELECT DISTINCT order_id
            FROM stage_orders
            WHERE trip_id = :trip_id
              AND leg = 'pickup'
            ORDER BY order_id ASC
            """
        ),
        {"trip_id": trip_id},
    ).fetchall()
    return [int(r[0]) for r in rows]


def count_available_orders_on_direction(session: Session, direction_id: int) -> int:
    """Свободные заказы на направлении (для reserve guard)."""
    n = session.execute(
        text(
            """
            SELECT COUNT(DISTINCT so.order_id)
            FROM stage_orders so
            JOIN orders o ON o.id = so.order_id
            WHERE so.direction_id = :direction_id
              AND so.leg = 'pickup'
              AND so.reserved_by_driver_id IS NULL
              AND so.trip_id IS NULL
              AND o.status IN ('order_parcel_confirmed', 'order_parcel_submitted')
            """
        ),
        {"direction_id": direction_id},
    ).scalar()
    return int(n or 0)


def count_active_driver_slots_on_direction(
    session: Session, direction_id: int, driver_user_id: int
) -> int:
    """Число active|loading резервов водителя на направлении."""
    n = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM driver_reservations
            WHERE driver_user_id = :driver_user_id
              AND direction_id = :direction_id
              AND status IN ('reservation_active', 'reservation_loading')
            """
        ),
        {"driver_user_id": driver_user_id, "direction_id": direction_id},
    ).scalar()
    return int(n or 0)


def list_orders_missing_trip_legs(
    session: Session, order_ids: list[int]
) -> list[int]:
    """
    Заказы без обеих ног pickup+delivery в stage_orders —
    такие нельзя надёжно привязать к trip.
    """
    if not order_ids:
        return []
    placeholders = ", ".join(f":oid_{i}" for i in range(len(order_ids)))
    params: dict[str, Any] = {f"oid_{i}": oid for i, oid in enumerate(order_ids)}
    rows = session.execute(
        text(
            f"""
            SELECT o.id
            FROM orders o
            LEFT JOIN stage_orders sp
              ON sp.order_id = o.id AND sp.leg = 'pickup'
            LEFT JOIN stage_orders sd
              ON sd.order_id = o.id AND sd.leg = 'delivery'
            WHERE o.id IN ({placeholders})
              AND (sp.order_id IS NULL OR sd.order_id IS NULL)
            ORDER BY o.id ASC
            """
        ),
        params,
    ).fetchall()
    return [int(r[0]) for r in rows]


def list_driver_trips(
    session: Session,
    driver_user_id: int,
    *,
    statuses: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Рейсы водителя; по умолчанию assigned + in_progress."""
    wanted = statuses or ["trip_assigned", "trip_in_progress"]
    placeholders = ", ".join(f":st_{i}" for i in range(len(wanted)))
    params: dict[str, Any] = {f"st_{i}": s for i, s in enumerate(wanted)}
    params["driver_user_id"] = driver_user_id
    rows = session.execute(
        text(
            f"""
            SELECT id, driver_user_id, from_city, to_city,
                   pickup_locker_id, delivery_locker_id,
                   status, description, active, created_at
            FROM trips
            WHERE driver_user_id = :driver_user_id
              AND active = 1
              AND status IN ({placeholders})
            ORDER BY id DESC
            """
        ),
        params,
    ).mappings().all()
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["order_ids"] = list_trip_order_ids(session, int(item["id"]))
        out.append(item)
    return out
