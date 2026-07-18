"""Courier domain SQL — session from Request Runtime / worker only."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def insert_order(
    session: Session,
    *,
    description: str,
    client_user_id: int,
    delivery_type: str = "courier",
    pickup_type: str = "courier",
    parcel_type: Optional[str] = None,
) -> int:
    result = session.execute(
        text(
            """
            INSERT INTO orders
                (status, description, delivery_type, pickup_type, parcel_type,
                 client_user_id, created_at, updated_at)
            VALUES
                ('order_created', :description, :delivery_type, :pickup_type, :parcel_type,
                 :client_user_id, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        ),
        {
            "description": description,
            "delivery_type": delivery_type,
            "pickup_type": pickup_type,
            "parcel_type": parcel_type,
            "client_user_id": client_user_id,
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
                   parcel_type, client_user_id, recipient_user_id,
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
            SELECT id, status, description, delivery_type, created_at
            FROM orders
            WHERE client_user_id = :uid
            ORDER BY id DESC
            LIMIT :lim
            """
        ),
        {"uid": client_user_id, "lim": limit},
    ).mappings().all()
    return [dict(r) for r in rows]
