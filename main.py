from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import os

from db_layer import DatabaseLayer, DbLayerError, FsmCallError
from models import (
    OrderCreateRequest, OrderResponse,
    TripCreateRequest, TripResponse,
    FsmActionRequest, ApiResponse,
    UserCreateRequest, LockerCreateRequest,
    CellCreateRequest, CellResponse, ButtonResponse
)

# ========== DATABASE SINGLETON ==========
db_instance: Optional[DatabaseLayer] = None

def get_db() -> DatabaseLayer:
    """Dependency для получения db instance"""
    if db_instance is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db_instance

# ========== LIFECYCLE ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup и shutdown события"""
    global db_instance
    
    # Startup
    try:
        db_instance = DatabaseLayer(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3307")),
            database=os.getenv("DB_NAME", "testdb"),
            user=os.getenv("DB_USER", "****"),
            password=os.getenv("DB_PASSWORD", "****"),
            echo=False
        )
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    #if db_instance:
     #   db_instance.close()
      #  print("🔌 Database connection closed")

# ========== FASTAPI APP ==========
app = FastAPI(
    title="FSM Emulator API",
    description="Backend для логистической FSM системы с автоматической обработкой таймаутов",
    version="2.0.0",
    lifespan=lifespan
)

# ========== CORS CONFIGURATION ==========
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://v0-fsm-emulator-interface.vercel.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ========== HEALTH CHECK ==========
@app.get("/")
async def root():
    return {"status": "ok", "message": "FSM Emulator API v2.0"}

@app.get("/health")
async def health_check(db: DatabaseLayer = Depends(get_db)):
    try:
        counters = db.get_log_counters()
        return {
            "status": "healthy",
            "database": "connected",
            "log_counters": {
                "fsm_errors": counters[0],
                "fsm_actions": counters[1],
                "hardware_commands": counters[2]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# ==================== ORDERS ENDPOINTS (НОВЫЕ) ====================

@app.post("/api/orders/create-smart", response_model=dict)
async def create_order_smart(
    source_cell_id: int,
    dest_cell_id: int,
    title: str = "Order from UI",
    pickup_type: str = "courier",    # ← Тип забора (self/courier)
    delivery_type: str = "courier",  # ← Тип доставки (self/courier)
    auto_assign_trip: bool = True,   # ← Автопривязка к рейсу
    db: DatabaseLayer = Depends(get_db)
):
    """
    Умное создание заказа с автопарсингом городов.
    
    Процесс:
    1. Парсит города из location_address постаматов
    2. Создаёт заказ с pickup_type и delivery_type
    3. Опционально: автоматически привязывает к рейсу
    
    Args:
        source_cell_id: ID ячейки отправления
        dest_cell_id: ID ячейки назначения
        title: Название заказа
        pickup_type: Как забрать у отправителя ('self' = сам, 'courier' = курьер1)
        delivery_type: Как доставить получателю ('self' = сам, 'courier' = курьер2)
        auto_assign_trip: Автоматически привязать к рейсу?
    
    Примеры комбинаций:
        - pickup='self', delivery='self' → Клиент сам несёт, получатель сам забирает
        - pickup='self', delivery='courier' → Клиент сам несёт, курьер2 доставляет
        - pickup='courier', delivery='self' → Курьер1 забирает, получатель сам забирает
        - pickup='courier', delivery='courier' → Полная курьерская доставка
    """
    try:
        # Шаг 1: Парсинг городов из адресов постаматов
        from_city = db.get_locker_city_by_cell(source_cell_id)
        to_city = db.get_locker_city_by_cell(dest_cell_id)
        
        # Шаг 2: Создание заказа
        order_id = db.create_order(
            description=title,
            source_cell_id=source_cell_id,
            dest_cell_id=dest_cell_id,
            from_city=from_city,
            to_city=to_city,
            pickup_type=pickup_type,
            delivery_type=delivery_type
        )
        
        # Шаг 3: Опционально - умная привязка к рейсу
        trip_id = None
        is_new_trip = False
        trip_message = "Order created without trip assignment"
        
        if auto_assign_trip:
            trip_id, is_new_trip, trip_message = db.assign_order_to_trip_smart(
                order_id, from_city, to_city
            )
        
        return {
            "success": True,
            "order_id": order_id,
            "trip_id": trip_id,
            "route": f"{from_city} → {to_city}",
            "from_city": from_city,
            "to_city": to_city,
            "pickup_type": pickup_type,
            "delivery_type": delivery_type,
            "is_new_trip": is_new_trip,
            "message": trip_message
        }
        
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания заказа: {str(e)}")


@app.post("/api/orders/create", response_model=dict)
async def create_order_manual(
    source_cell_id: int,
    dest_cell_id: int,
    from_city: str,
    to_city: str,
    title: str = "Order",
    pickup_type: str = "courier",
    delivery_type: str = "courier",
    db: DatabaseLayer = Depends(get_db)
):
    """
    Создание заказа с явным указанием городов (без парсинга).
    
    Используйте этот endpoint если хотите задать города вручную.
    """
    try:
        order_id = db.create_order(
            description=title,
            source_cell_id=source_cell_id,
            dest_cell_id=dest_cell_id,
            from_city=from_city,
            to_city=to_city,
            pickup_type=pickup_type,
            delivery_type=delivery_type
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "route": f"{from_city} → {to_city}",
            "pickup_type": pickup_type,
            "delivery_type": delivery_type
        }
        
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/start-flow", response_model=dict)
async def start_order_flow(
    order_id: int,
    user_id: int = 0,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Запустить FSM flow заказа (первая развилка на основе pickup_type).
    
    Автоматически выбирает FSM переход:
    - pickup_type='self' → order_reserve_for_client_A_to_B
    - pickup_type='courier' → order_reserve_for_courier_A_to_B
    
    Args:
        order_id: ID заказа
        user_id: ID курьера (если pickup_type='courier')
    """
    try:
        db.start_order_flow(order_id, user_id)
        order = db.get_order(order_id)
        
        return {
            "success": True,
            "order_id": order_id,
            "status": order["status"],
            "pickup_type": order["pickup_type"],
            "message": f"FSM flow запущен для заказа {order_id}"
        }
        
    except (DbLayerError, FsmCallError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/handle-parcel-confirmed", response_model=dict)
async def handle_parcel_confirmed(
    order_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Обработка после попадания посылки в постамат2 (вторая развилка на основе delivery_type).
    
    НЕ делает FSM переходов! Только логирует путь:
    - delivery_type='self' → получатель сам заберёт
    - delivery_type='courier' → будет доступен на бирже для курьера2
    
    Вызывать после FSM перехода в order_parcel_confirmed.
    """
    try:
        db.handle_parcel_confirmed(order_id)
        order = db.get_order(order_id)
        
        return {
            "success": True,
            "order_id": order_id,
            "status": order["status"],
            "delivery_type": order["delivery_type"],
            "message": "Путь заказа определён на основе delivery_type"
        }
        
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders/by-route", response_model=List[dict])
async def get_orders_by_route(
    from_city: str,
    to_city: str,
    statuses: Optional[str] = None,
    db: DatabaseLayer = Depends(get_db)
):
    """Получить заказы по маршруту (опционально фильтровать по статусам)"""
    try:
        status_list = statuses.split(",") if statuses else None
        orders = db.get_orders_for_route(from_city, to_city, status_list)
        return orders
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders/{order_id}", response_model=dict)
async def get_order(order_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить заказ по ID"""
    try:
        order = db.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders", response_model=List[dict])
async def get_all_orders(
    statuses: Optional[str] = None,
    db: DatabaseLayer = Depends(get_db),
):
    """
    Получить все заказы без привязки к маршруту.
    Опционально: фильтр по статусам, через запятую, например:
    ?statuses=order_created,order_parcel_confirmed
    """
    try:
        status_list = statuses.split(",") if statuses else None
        orders = db.get_all_orders(status_list)
        return orders
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== БИРЖИ КУРЬЕРОВ (НОВЫЕ) ====================

@app.get("/api/courier/exchange-pickup", response_model=dict)
async def get_exchange_orders_pickup(
    city: Optional[str] = None,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Биржа заказов для курьера1 (забор от клиента).
    
    Показывает заказы:
    - Статус: order_created
    - Тип забора: pickup_type='courier'
    - Местоположение: source_cell (откуда забрать)
    
    Args:
        city: Фильтр по городу отправления (опционально)
    """
    try:
        orders = db.get_available_orders_for_courier1(city)
        return {
            "type": "pickup",
            "description": "Заказы для курьера1 (забор от клиента)",
            "count": len(orders),
            "orders": orders
        }
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/courier/exchange-delivery", response_model=dict)
async def get_exchange_orders_delivery(
    city: Optional[str] = None,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Биржа заказов для курьера2 (доставка получателю).
    
    Показывает заказы:
    - Статус: order_parcel_confirmed
    - Тип доставки: delivery_type='courier'
    - Местоположение: dest_cell (откуда забрать для доставки)
    
    Args:
        city: Фильтр по городу назначения (опционально)
    """
    try:
        orders = db.get_available_orders_for_courier2(city)
        return {
            "type": "delivery",
            "description": "Заказы для курьера2 (доставка получателю)",
            "count": len(orders),
            "orders": orders
        }
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== TRIPS ENDPOINTS ====================

@app.post("/api/trips", response_model=ApiResponse)
async def create_trip(request: TripCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать рейс"""
    try:
        trip_id = db.create_trip(
            from_city=request.from_city,
            to_city=request.to_city,
            driver_user_id=request.driver_user_id,
            description=request.description,
            active=request.active
        )
        
        return ApiResponse(
            success=True,
            message="Trip created",
            data={"trip_id": trip_id}
        )
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}", response_model=dict)
async def get_trip(trip_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить рейс по ID"""
    try:
        trip = db.get_trip(trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found")
        return trip
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}/orders", response_model=List[int])
async def get_trip_orders(trip_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить список order_id рейса"""
    try:
        order_ids = db.get_trip_orders(trip_id)
        return order_ids
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/trips/{trip_id}/assign-order/{order_id}", response_model=ApiResponse)
async def assign_order_to_trip(
    trip_id: int,
    order_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """Привязать заказ к рейсу (ручной метод)"""
    try:
        success, msg = db.assign_order_to_trip(order_id, trip_id)
        return ApiResponse(success=success, message=msg)
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/assign-trip-smart", response_model=dict)
async def assign_trip_smart(
    order_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Умная привязка существующего заказа к рейсу.
    
    Автоматически найдёт подходящий рейс или создаст новый.
    """
    try:
        order = db.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        
        trip_id, is_new, msg = db.assign_order_to_trip_smart(
            order_id, 
            order["from_city"], 
            order["to_city"]
        )
        
        return {
            "success": True,
            "order_id": order_id,
            "trip_id": trip_id,
            "is_new_trip": is_new,
            "message": msg
        }
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/trips/{trip_id}/activate", response_model=dict)
async def activate_trip(
    trip_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Ручная активация конкретного рейса.
    Активирует рейс даже если не достигнут порог заказов.
    """
    try:
        db.activate_trip_manual(trip_id) 
        trip = db.get_trip(trip_id)
        
        return {
            "success": True,
            "trip_id": trip_id,
            "active": trip["active"],
            "message": f"Рейс {trip_id} активирован вручную"
        }
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка активации рейса: {str(e)}")

# ==================== TIMEOUTS (НОВЫЙ РАЗДЕЛ) ====================

@app.post("/api/timeouts/process", response_model=dict)
async def process_timeouts(
    reservation_timeout_sec: int = 1800,
    trip_timeout_hours: float = 24.0,
    trip_max_orders: int = 5,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Обработка таймаутов (эмуляция планировщика).
    
    На продакшене вызывается автоматически через крон каждые 30 секунд.
    В тестах - вручную через этот endpoint.
    
    Args:
        reservation_timeout_sec: Таймаут резерва заказа (по умолчанию 30 минут)
        trip_timeout_hours: Таймаут активации рейса (по умолчанию 24 часа)
        trip_max_orders: Максимум заказов для автоактивации рейса
    """
    try:
        orders_processed = db.check_and_process_reservation_timeouts(reservation_timeout_sec)
        trips_activated = db.update_trip_active_flags(trip_max_orders, trip_timeout_hours)
        
        return {
            "success": True,
            "orders_processed": orders_processed,
            "trips_activated": trips_activated,
            "message": f"Обработано заказов: {orders_processed}, Активировано рейсов: {trips_activated}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки таймаутов: {str(e)}")

# ==================== FSM ACTIONS ====================

@app.post("/api/fsm/action", response_model=ApiResponse)
async def perform_fsm_action(request: FsmActionRequest, db: DatabaseLayer = Depends(get_db)):
    """Выполнить FSM действие"""
    try:
        result = db.call_fsm_action(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            action_name=request.action_name,
            user_id=request.user_id,
            extra_id=request.extra_id
        )
        
        return ApiResponse(
            success=True,
            message=f"FSM action '{request.action_name}' executed"
        )
    except FsmCallError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/fsm/buttons", response_model=List[ButtonResponse])
async def get_buttons(
    user_role: str,
    entity_type: str,
    entity_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """Получить доступные кнопки для роли"""
    try:
        buttons = db.get_buttons(user_role, entity_type, entity_id)
        return [ButtonResponse(**btn) for btn in buttons]
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== LOCKERS / CELLS ====================

@app.post("/api/lockers", response_model=ApiResponse)
async def create_locker(request: LockerCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать постамат"""
    try:
        db.create_locker(
            locker_id=request.locker_id,
            locker_code=request.locker_code,
            location_address=request.location_address,
            model_id=request.model_id
        )
        return ApiResponse(success=True, message="Locker created")
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/lockers/cells", response_model=ApiResponse)
async def create_cell(request: CellCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать ячейку"""
    try:
        cell_id = db.create_locker_cell(
            locker_id=request.locker_id,
            cell_code=request.cell_code,
            cell_type=request.cell_type
        )
        return ApiResponse(
            success=True,
            message="Cell created",
            data={"cell_id": cell_id}
        )
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))
        

@app.get("/api/lockers", response_model=List[dict])
async def list_lockers(db: DatabaseLayer = Depends(get_db)):
    try:
        return db.get_lockers()
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/lockers/{locker_id}/cells", response_model=List[CellResponse])
async def get_cells_by_status(
    locker_id: int,
    status: str = "locker_free",
    db: DatabaseLayer = Depends(get_db)
):
    """Получить ячейки постамата по статусу"""
    try:
        cells = db.get_locker_cells_by_status(locker_id, status)
        return [CellResponse(**cell) for cell in cells]
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/cells/{cell_id}/city", response_model=dict)
async def get_cell_city(
    cell_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить город по ID ячейки (парсинг адреса).
    
    Пример: "Москва, Ленина 10" → "Москва"
    """
    try:
        city = db.get_locker_city_by_cell(cell_id)
        return {"cell_id": cell_id, "city": city}
    except DbLayerError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ==================== USERS ====================

@app.post("/api/users", response_model=ApiResponse)
async def create_user(request: UserCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать пользователя"""
    try:
        db.create_user(
            user_id=request.user_id,
            name=request.name,
            role=request.role
        )
        return ApiResponse(success=True, message="User created")
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}/role")
async def get_user_role(user_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить роль пользователя"""
    try:
        role = db.get_user_role(user_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return {"user_id": user_id, "role": role}
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== UTILITIES ====================

@app.post("/api/test/clear", response_model=ApiResponse)
async def clear_test_data(db: DatabaseLayer = Depends(get_db)):
    """Очистить тестовые данные"""
    try:
        db.clear_test_data()
        return ApiResponse(success=True, message="Test data cleared")
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/test/log-counters")
async def get_log_counters(db: DatabaseLayer = Depends(get_db)):
    """Получить счётчики логов"""
    try:
        error_count, fsm_count, hw_count = db.get_log_counters()
        return {
            "fsm_errors": error_count,
            "fsm_actions": fsm_count,
            "hardware_commands": hw_count
        }
    except DbLayerError as e:
        raise HTTPException(status_code=400, detail=str(e))
