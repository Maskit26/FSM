"""Courier domain SQL — session from Request Runtime / worker only."""

from __future__ import annotations

import math
import re
from typing import Any, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


def _city_hint(address: str) -> str:
    """First comma-separated segment: 'Москва, ул. Тверская, д. 1' → 'Москва'."""
    return address.split(",")[0].strip()


def _haversine_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
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
    Nearest locker with a free cell of cell_size.
    Prefer geo distance when address lat/lng given and locker has coords;
    else match by city hint + address text against lockers.location_address.
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
