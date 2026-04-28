from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict, Literal

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
    recipient_user_id: int
    parcel_type: str
    cell_size: str
    sender_delivery: str
    recipient_delivery: str

class TripCreateRequest(BaseModel):
    from_city: str
    to_city: str
    pickup_locker_id: int
    delivery_locker_id: int
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

class FsmEnqueueRequest(BaseModel):
    entity_type: str        # 'order' | 'trip' ...
    entity_id: int
    process_name: str       # например 'order_assign_courier1'    
    user_id: int
    target_user_id: Optional[int] = None
    target_role: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

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

# ========== DIRECTION MODELS ==========
class DirectionResponse(BaseModel):
    id: int
    status: str
    from_city: str
    to_city: str
    pickup_locker_id: int
    delivery_locker_id: int
    orders_total: int
    orders_available: int
    orders_reserved: int

class DirectionReserveRequest(BaseModel):
    direction_id: int
    driver_user_id: int
    capacity: int

class DirectionReserveResponse(BaseModel):
    success: bool
    reservation_id: Optional[int] = None
    reserved_count: int
    message: str

class DriverReservationResponse(BaseModel):
    id: int
    direction_id: int
    from_city: str
    to_city: str
    reserved_count: int
    requested_count: int
    reserved_at: Optional[str] = None
    expires_at: Optional[str] = None
    status: str
    reserved_order_ids: Optional[List[int]] = None

class DirectionSlotActionRequest(BaseModel):
    direction_id: int
    driver_user_id: int
    reservation_id: Optional[int] = None

# ==================== CORE USER MAPPING ====================
class UserRegisterRequest(BaseModel):
    """Запрос на регистрацию пользователя"""
    name: str
    phone: str
    email: Optional[str] = None
    role_name: str = "client"
    city: Optional[str] = None
    password: str

class UserRegisterResponse(BaseModel):
    """Ответ после регистрации"""
    user_id: int
    core_user_id: Optional[int] = None
    performer_type: Optional[str] = None
    core_sync_status: str  # success, failed, unavailable
    message: str

class UserLoginRequest(BaseModel):
    login: str
    password: str
    type: str = "phone"

class UserLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user_id: Optional[int] = None
    core_user_id: Optional[int] = None
    role: Optional[str] = None
    message: str

class LogoutRequest(BaseModel):
    user_id: int

    # ========== CORE ORDER MODELS ==========
class CoreOrderCreateRequest(BaseModel):
    """Данные для создания заказа в Core (параметры для /api/v1/drive)."""
    b_start_address: str
    b_destination_address: str
    city_start: Optional[str] = None
    city_destination: Optional[str] = None
    b_payment_way: int = 2
    b_start_datetime: str = "any"
    b_passengers_count: int = 1
    b_luggage_count: int = 0
    b_options: Optional[str] = None

class CoreOrderCreateResponse(BaseModel):
    """Ответ Core после создания заказа."""
    code: str
    status: str
    data: Dict[str, Any]

# ==================== Создание авто ================
class CarType(str, Enum):
    COURIER = "courier"
    DRIVER = "driver"

class CarCreateRequest(BaseModel):
    car_type: CarType
    seats: int = 1
    custom_body_ru: Optional[str] = None
    custom_body_en: Optional[str] = None
    custom_make_ru: Optional[str] = None
    custom_make_en: Optional[str] = None
    custom_model_ru: Optional[str] = None
    custom_model_en: Optional[str] = None
    custom_model_year: Optional[int] = None
    custom_model_doors: Optional[int] = None

# =============== верификация пользователя =============
class UserVerifyStateRequest(BaseModel):
    """Запрос на изменение статуса верификации."""
    local_user_id: int = Field(..., description="ID пользователя, которому меняем статус")
    admin_local_user_id: int = Field(..., description="ID администратора, от чьего имени запрос")
    u_check_state: int = Field(..., ge=0, le=4, description="Новый статус (0-4)")