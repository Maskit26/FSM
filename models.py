from pydantic import BaseModel
from typing import Optional, List

# ========== REQUEST MODELS ==========
class OrderCreateRequest(BaseModel):
    description: str
    from_city: str
    to_city: str
    source_cell_id: Optional[int] = None
    dest_cell_id: Optional[int] = None
    delivery_type: Optional[str] = None

class ClientCreateOrderRequest(BaseModel):
    client_user_id: int
    parcel_type: str
    cell_size: str
    sender_delivery: str
    recipient_delivery: str

class TripCreateRequest(BaseModel):
    from_city: str
    to_city: str
    driver_user_id: Optional[int] = None
    description: Optional[str] = None
    active: int = 0

class FsmActionRequest(BaseModel):
    entity_type: str
    entity_id: int
    action_name: str
    user_id: int
    extra_id: Optional[str] = None

class UserCreateRequest(BaseModel):
    user_id: int
    name: str
    role: str

class LockerCreateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    locker_id: int
    locker_code: str
    location_address: str
    model_id: int = 1

class CellCreateRequest(BaseModel):
    locker_id: int
    cell_code: str
    cell_type: str = "S"

# ========== RESPONSE MODELS ==========
class OrderResponse(BaseModel):
    id: int
    status: str
    description: str
    pickup_type: Optional[str] = None
    delivery_type: Optional[str] = None
    from_city: str
    to_city: str
    source_cell_id: Optional[int]
    dest_cell_id: Optional[int]

class TripResponse(BaseModel):
    id: int
    status: str
    active: int
    from_city: str
    to_city: str
    driver_user_id: Optional[int]

class CellResponse(BaseModel):
    id: int
    cell_code: str
    cell_type: str
    status: str
    current_order_id: Optional[int]

class ButtonResponse(BaseModel):
    button_name: str
    is_enabled: bool

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
