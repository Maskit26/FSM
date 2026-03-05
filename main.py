import os
from typing import Generator, List, Optional, Dict, Any
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fsm_engine import PROCESS_DEFS
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from db_layer import DatabaseLayer, DbLayerError, FsmCallError
from models import (
    OrderCreateRequest, OrderResponse,
    TripCreateRequest, TripResponse,
    FsmActionRequest, ApiResponse,
    UserCreateRequest, LockerCreateRequest,
    CellCreateRequest, CellResponse, ButtonResponse,
    ClientCreateOrderRequest, FsmEnqueueRequest,
)

# ======================
# ЗАГРУЗКА ENV
# ======================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "fsm")
DB_PASSWORD = os.getenv("DB_PASSWORD", "6eF1zb")

# ======================
# SQLALCHEMY ENGINE И SESSIONMAKER
# ======================
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======================
# CONTEXT-MANAGER ДЛЯ СЕССИИ (API READ-ONLY)
# ======================
@contextmanager
def get_db_session(read_only: bool = True) -> Generator[Session, None, None]:
    """
    Контекст для сессии SQLAlchemy.
    read_only=True → commit не делаем, rollback только при ошибке.
    read_only=False → можно коммитить (для воркера или API, который пишет в БД)
    """
    session: Session = SessionLocal()
    try:
        yield session
        if not read_only:
            session.commit()
        else:
            session.rollback()  # read-only rollback для очистки транзакции
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ======================
# DEPENDENCY ДЛЯ API
# ======================
def get_db() -> Generator[DatabaseLayer, None, None]:
    """Возвращает stateless экземпляр DatabaseLayer (без сессии!)."""
    yield DatabaseLayer()

# ======================
# FASTAPI APP
# ======================
app = FastAPI(
    title="FSM Emulator API",
    description="Backend для логистической FSM системы с автоматической обработкой таймаутов",
    version="2.0.0",
)

# ======================
# CORS
# ======================
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    
    allowed_origins = [
        "https://super-lamp.vercel.app",
        "http://91.135.156.173:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://v0-fsm-emulator-interface.vercel.app"
    ]
    
    if request.method == "OPTIONS":
        # Preflight запрос
        headers = {
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        if origin in allowed_origins:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
        
        return Response(status_code=204, headers=headers)

    # Обычные запросы
    response = await call_next(request)
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# ======================
# ОБРАБОТЧИК DB ERRORS
# ======================
def handle_db_error(exc: DbLayerError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )

# ========== HEALTH CHECK ==========
@app.get("/")
async def root():
    return {"status": "ok", "message": "FSM Emulator API v2.0"}

@app.get("/health")
async def health_check(db: DatabaseLayer = Depends(get_db)):
    with get_db_session(read_only=True) as session:
        try:
            counters = db.get_log_counters(session)
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
    with get_db_session(read_only=False) as session:
        try:
            # Шаг 1: Парсинг городов из адресов постаматов
            from_city = db.get_locker_city_by_cell(session, source_cell_id)
            to_city = db.get_locker_city_by_cell(session, dest_cell_id)
            
            # Шаг 2: Создание заказа
            order_id = db.create_order(
                session,
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
                    session, order_id, from_city, to_city
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


@app.post("/api/client/create_order_request", response_model=ApiResponse)
async def create_order_request(
    request: ClientCreateOrderRequest,
    db: DatabaseLayer = Depends(get_db)
):
    with get_db_session(read_only=False) as session:
        try:
            request_id = db.create_order_request_and_fsm(
                session,
                client_user_id=request.client_user_id,
                recipient_user_id=request.recipient_user_id,
                parcel_type=request.parcel_type,
                cell_size=request.cell_size,
                sender_delivery=request.sender_delivery,
                recipient_delivery=request.recipient_delivery
            )
            return ApiResponse(
                success=True,
                message="Заявка создана, обработка начата",
                data={"request_id": request_id}
            )
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/orders/create", response_model=Dict)
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

    Args:
        source_cell_id: ID ячейки отправления
        dest_cell_id: ID ячейки назначения
        from_city: Город отправления
        to_city: Город назначения
        title: Название заказа
        pickup_type: Как забрать у отправителя ('self' = сам, 'courier' = курьер)
        delivery_type: Как доставить получателю ('self' = сам, 'courier' = курьер)
    
    Returns:
        Dict с результатом создания заказа, route и типами доставки/забора
    """
    with get_db_session(read_only=False) as session:
        try:
            order_id = db.create_order(
                session,
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


@app.post("/api/orders/{order_id}/start-flow", response_model=Dict)
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

    Returns:
        Dict с текущим статусом заказа и информацией о pickup_type
    """
    with get_db_session(read_only=False) as session:
        try:
            db.start_order_flow(session, order_id, user_id)
            order = db.get_order(session, order_id)
            return {
                "success": True,
                "order_id": order_id,
                "status": order["status"],
                "pickup_type": order["pickup_type"],
                "message": f"FSM flow запущен для заказа {order_id}"
            }
        except (DbLayerError, FsmCallError) as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orders/{order_id}/handle-parcel-confirmed", response_model=Dict)
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

    Args:
        order_id: ID заказа

    Returns:
        Dict с текущим статусом заказа, типом доставки и сообщением о пути
    """
    with get_db_session(read_only=False) as session:
        try:
            db.handle_parcel_confirmed(session, order_id)
            order = db.get_order(session, order_id)
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
    """
    Получить заказы по маршруту (опционально фильтровать по статусам).
    
    Args:
        from_city: город отправления
        to_city: город назначения
        statuses: опциональный фильтр по статусам через запятую, например "order_created,order_parcel_confirmed"
    
    Returns:
        Список заказов, соответствующих маршруту и статусу
    """
    with get_db_session(read_only=True) as session:
        try:
            status_list = statuses.split(",") if statuses else None
            return db.get_orders_for_route(session, from_city, to_city, status_list)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


# == получение информации о заказах/рейсах для клиента/курьера/водителя ====
@app.get("/api/orders/user/{user_id}", response_model=List[dict])
async def get_user_orders(
    user_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить все заказы пользователя по его ID.
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Список заказов пользователя
    """
    with get_db_session(read_only=True) as session:
        try:
            return db.get_user_orders(session, user_id)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders/courier/{courier_id}", response_model=List[dict])
async def get_courier_orders_endpoint(
    courier_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить все заказы курьера по его ID.
    
    Args:
        courier_id: ID курьера
    
    Returns:
        Список заказов курьера с информацией о плече (pickup/delivery)
    """
    with get_db_session(read_only=True) as session:
        try:
            return db.get_courier_orders(session, courier_id)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/trips/driver/{driver_id}", response_model=List[dict])
async def get_driver_trips_endpoint(
    driver_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить активные рейсы водителя с заказами внутри.
    
    Args:
        driver_id: ID водителя
    
    Returns:
        Список рейсов, внутри каждого — список заказов
    """
    with get_db_session(read_only=True) as session:
        try:
            return db.get_driver_trips_with_orders(session, driver_id)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/fsm/user-errors", response_model=dict)
async def get_user_fsm_errors(
    user_id: int,
    limit: int = 50,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить последние FSM-ошибки для пользователя.
    
    """
    with get_db_session(read_only=True) as session:
        try:
            errors = db.get_user_fsm_errors(session, user_id, limit)
            
            return {
                "success": True,
                "errors": errors,
                "count": len(errors)
            }
            
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Для получения 6-тизначного пин кода. Для теста, удалить на продакшне
@app.post("/api/access-code/view", response_model=Dict[str, Any])
async def view_access_code(
    order_id: int,
    leg: str,
    user_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить PIN-код для доступа к ячейке (кнопка 'Посмотреть код'). 
    Для тетса. Удалить на продакшене
    """
    with get_db_session(read_only=True) as session:
        try:
            # Проверка авторизации
            order = db.get_order(session, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
            
            if leg == "pickup":
                if order["pickup_type"] == "self":
                    authorized_id = order["client_user_id"]
                else:
                    stage = db.get_stage_order(session, order_id, "pickup")
                    authorized_id = stage.courier_user_id if stage else None
            else:
                if order["delivery_type"] == "self":
                    authorized_id = order.get("recipient_user_id")
                else:
                    stage = db.get_stage_order(session, order_id, "delivery")
                    authorized_id = stage.courier_user_id if stage else None
            
            if authorized_id != user_id:
                raise HTTPException(status_code=403, detail="USER_NOT_AUTHORIZED")
            
            pin = db.get_access_token_pin(session, order_id, leg, user_id)
            
            if not pin:
                raise HTTPException(status_code=404, detail="CODE_NOT_FOUND_OR_EXPIRED")
            
            return {
                "success": True,
                "pin": pin,
                "order_id": order_id,
                "leg": leg
            }
            
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/orders/{order_id}", response_model=dict)
async def get_order(order_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить заказ по ID"""
    with get_db_session(read_only=True) as session:
        try:
            order = db.get_order(session, order_id)
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
    with get_db_session(read_only=True) as session:
        try:
            status_list = statuses.split(",") if statuses else None
            orders = db.get_all_orders(session, status_list)
            return orders
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

# ==================== БИРЖИ ====================

@app.get("/api/courier/exchange", response_model=dict)
async def get_courier_exchange(
    courier_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    with get_db_session(read_only=True) as session:
        user = db.get_user_by_id(session, courier_id)
        if not user or user["role_name"] != "courier":
            raise HTTPException(status_code=400, detail="Invalid courier ID")

        orders_data = db.get_all_available_orders_for_courier(session, user["city"])
        all_orders = orders_data["all"]

        return {
            "courier_id": courier_id,
            "city": user["city"],
            "orders": all_orders,  # ← каждый заказ содержит "type": "pickup" или "delivery"
            "counts": {
                "pickup": len(orders_data["pickup"]),
                "delivery": len(orders_data["delivery"]),
                "total": len(all_orders)
            }
        }

@app.get("/api/driver/exchange", response_model=List[dict])
async def get_driver_exchange_trips(
    city: str,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Возвращает рейсы, доступные для взятия водителем из указанного города.
    Условия:
    - trips.from_city = :city
    - trips.status = 'trip_created'
    - trips.active = 1
    """
    with get_db_session(read_only=True) as session:
        trips = db.get_available_trips_for_driver_exchange(session, city)
    return trips

# ==================== Универсальное действие ====================

@app.post("/api/fsm/enqueue", response_model=ApiResponse)
async def enqueue_fsm(request: FsmEnqueueRequest, db: DatabaseLayer = Depends(get_db)):
    with get_db_session(read_only=False) as session:
        if request.process_name not in PROCESS_DEFS:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимое имя процесса: '{request.process_name}'. "
                       f"Доступные процессы: {', '.join(sorted(PROCESS_DEFS.keys()))}"
            )
        # 1) Проверяем пользователя (пока userid приходит от фронта в body)
        role = db.get_user_role(session, request.user_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

        # 2) ОПРЕДЕЛЯЕМ fsm_state по process_name
        fsm_state = "PENDING"

        # 2) Создаём/обновляем инстанс (заявку) в serverfsminstances
        try:
            instance_id = db.enqueue_fsm_instance(
                session,
                entity_type=request.entity_type,
                entity_id=request.entity_id,
                process_name=request.process_name,
                fsm_state=fsm_state,
                requested_by_user_id=request.user_id,
                requested_user_role=role,
                target_user_id=request.target_user_id,
                target_role=request.target_role,
                metadata=request.metadata,
            )
            return ApiResponse(success=True, message="ENQUEUED", data={"instance_id": instance_id})

        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# ==================== TRIPS ENDPOINTS ====================

@app.post("/api/trips", response_model=ApiResponse)
async def create_trip(request: TripCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать рейс"""
    with get_db_session(read_only=False) as session:
        try:
            trip_id = db.create_trip(
                session,
                from_city=request.from_city,
                to_city=request.to_city,
                pickup_locker_id=request.pickup_locker_id,  # ← добавлено (предполагается, что есть в модели)
                delivery_locker_id=request.delivery_locker_id,  # ← добавлено
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
    with get_db_session(read_only=True) as session:
        try:
            trip = db.get_trip(session, trip_id)
            if not trip:
                raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found")
            return trip
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trips/{trip_id}/orders", response_model=List[dict])
async def get_trip_orders(trip_id: int, db: DatabaseLayer = Depends(get_db)):
    """Получить заказы рейса (для драйвера на бирже)."""
    with get_db_session(read_only=True) as session:
        try:
            orders = db.get_trip_orders(session, trip_id)
            return orders
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/trips/{trip_id}/assign-order/{order_id}", response_model=ApiResponse)
async def assign_order_to_trip(
    trip_id: int,
    order_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """Привязать заказ к рейсу (ручной метод)"""
    with get_db_session(read_only=False) as session:
        try:
            success, msg = db.assign_order_to_trip(session, order_id, trip_id)
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
    with get_db_session(read_only=False) as session:
        try:
            order = db.get_order(session, order_id)
            if not order:
                raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
            
            trip_id, is_new, msg = db.assign_order_to_trip_smart(
                session,
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
    with get_db_session(read_only=False) as session:
        try:
            db.activate_trip_manual(session, trip_id) 
            trip = db.get_trip(session, trip_id)
            
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

# ==================== TIMEOUTS/Ошибки ====================

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
    with get_db_session(read_only=False) as session:
        try:
            orders_processed = db.check_and_process_reservation_timeouts(
                session, reservation_timeout_sec
            )
            trips_activated = db.update_trip_active_flags(
                session, trip_max_orders, trip_timeout_hours
            )
            
            return {
                "success": True,
                "orders_processed": orders_processed,
                "trips_activated": trips_activated,
                "message": f"Обработано заказов: {orders_processed}, Активировано рейсов: {trips_activated}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка обработки таймаутов: {str(e)}")

@app.get("/api/error-types", response_model=List[str])
async def get_error_types(db: DatabaseLayer = Depends(get_db)):
    """Получить список доступных типов ошибок."""
    with get_db_session(read_only=True) as session:
        try:
            return db.get_error_types(session)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

# ==================== FSM ACTIONS ====================

@app.post("/api/fsm/action", response_model=ApiResponse)
async def perform_fsm_action(request: FsmActionRequest, db: DatabaseLayer = Depends(get_db)):
    """Выполнить FSM действие"""
    with get_db_session(read_only=False) as session:
        try:
            result = db.call_fsm_action(
                session,
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
    with get_db_session(read_only=True) as session:
        try:
            buttons = db.get_buttons(session, user_role, entity_type, entity_id)
            return [ButtonResponse(**btn) for btn in buttons]
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

# ==================== LOCKERS / CELLS ====================

@app.post("/api/lockers", response_model=ApiResponse)
async def create_locker(request: LockerCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать постамат"""
    with get_db_session(read_only=False) as session:
        try:
            db.create_locker(
                session,
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
    with get_db_session(read_only=False) as session:
        try:
            cell_id = db.create_locker_cell(
                session,
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
    with get_db_session(read_only=True) as session:
        try:
            return db.get_lockers(session)
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/lockers/{locker_id}/cells", response_model=List[CellResponse])
async def get_cells_by_status(
    locker_id: int,
    status: str = "locker_free",
    db: DatabaseLayer = Depends(get_db)
):
    """Получить ячейки постамата по статусу"""
    with get_db_session(read_only=True) as session:
        try:
            cells = db.get_locker_cells_by_status(session, locker_id, status)
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
    with get_db_session(read_only=True) as session:
        try:
            city = db.get_locker_city_by_cell(session, cell_id)
            return {"cell_id": cell_id, "city": city}
        except DbLayerError as e:
            raise HTTPException(status_code=404, detail=str(e))

# ==================== USERS ====================

@app.post("/api/users", response_model=ApiResponse)
async def create_user(request: UserCreateRequest, db: DatabaseLayer = Depends(get_db)):
    """Создать пользователя"""
    with get_db_session(read_only=False) as session:
        try:
            db.create_user(
                session,
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
    with get_db_session(read_only=True) as session:
        try:
            role = db.get_user_role(session, user_id)
            if not role:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            return {"user_id": user_id, "role": role}
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users", response_model=List[dict])
async def get_all_users(
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить всех пользователей из таблицы users.
    
    Returns:
        Список всех пользователей с полями: id, name, role_name, city, phone
    """
    with get_db_session(read_only=True) as session:
        try:
            users = db.get_all_users(session)
            return users
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

# ==================== FSM ЭМУЛЯТОР ====================
@app.get("/api/fsm/emulator/entities", response_model=List[dict])
async def get_emulator_entities(
    entity_type: Optional[str] = Query(default="all", description="Тип сущности: order, trip, locker, all"),
    status: Optional[str] = Query(default="all", description="Статус: order_created, trip_assigned, all"),
    limit: int = Query(default=50, ge=1, le=100),
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить список сущностей для таблицы эмулятора.
    
    Args:
        entity_type: Тип сущности ('order', 'trip', 'locker', 'all')
        status: Фильтр по статусу ('all' = без фильтрации)
        limit: Максимальное количество записей
    """
    with get_db_session(read_only=True) as session:
        try:
            # Если "all" — получаем все типы сущностей
            if entity_type == "all" or not entity_type:
                all_entities = []
                
                # Получаем заказы
                orders = db.get_emulator_entities(session, "order", limit)
                for order in orders:
                    order["entity_type"] = "order"  # ← Добавляем entity_type в ответ
                    all_entities.append(order)
                
                # Получаем рейсы
                trips = db.get_emulator_entities(session, "trip", limit // 2)
                for trip in trips:
                    trip["entity_type"] = "trip"
                    all_entities.append(trip)
                
                # Получаем ячейки
                lockers = db.get_emulator_entities(session, "locker", limit // 2)
                for locker in lockers:
                    locker["entity_type"] = "locker"
                    all_entities.append(locker)
                
                # Фильтр по статусу
                if status != "all" and status:
                    all_entities = [e for e in all_entities if e.get("status") == status]
                
                # Сортировка и лимит
                all_entities.sort(key=lambda x: x.get("id", 0), reverse=True)
                entities = all_entities[:limit]
            else:
                # Один тип сущности
                entities = db.get_emulator_entities(session, entity_type, limit)
                for entity in entities:
                    entity["entity_type"] = entity_type  # ← Добавляем entity_type в ответ
                
                # Фильтр по статусу
                if status != "all" and status:
                    entities = [e for e in entities if e.get("status") == status]
            
            return entities
            
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/fsm/emulator/entities/{entity_type}/{entity_id}/actions", response_model=dict)
async def get_entity_actions(
    entity_type: str,
    entity_id: int,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить доступные FSM-действия для сущности.
    Заполняет dropdown в колонке Available Actions.
    """
    with get_db_session(read_only=True) as session:
        try:
            current_state = db.get_entity_current_state(session, entity_type, entity_id)
            
            if not current_state:
                raise HTTPException(status_code=404, detail=f"Сущность {entity_type}/{entity_id} не найдена")
            
            actions = db.get_available_fsm_actions(session, entity_type, current_state)
            
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "current_state": current_state,
                "available_actions": actions
            }
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/fsm/emulator/entities/{entity_type}/{entity_id}/history", response_model=dict)
async def get_entity_history(
    entity_type: str,
    entity_id: int,
    limit: int = 50,
    db: DatabaseLayer = Depends(get_db)
):
    """
    Получить историю FSM-переходов.
    Открывается при клике на Current State в таблице.
    """
    with get_db_session(read_only=True) as session:
        try:
            history = db.get_fsm_action_history(session, entity_type, entity_id, limit)
            
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "history": history,
                "count": len(history)
            }
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))

# ==================== UTILITIES ====================

@app.post("/api/test/clear", response_model=ApiResponse)
async def clear_test_data(db: DatabaseLayer = Depends(get_db)):
    """Очистить тестовые данные"""
    # Примечание: clear_test_data использует прямое подключение к БД,
    # поэтому сессия не требуется. Но для единообразия оборачиваем в контекст.
    with get_db_session(read_only=False) as session:
        try:
            db.clear_test_data()
            return ApiResponse(success=True, message="Test data cleared")
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/test/log-counters")
async def get_log_counters(db: DatabaseLayer = Depends(get_db)):
    """Получить счётчики логов"""
    with get_db_session(read_only=True) as session:
        try:
            error_count, fsm_count, hw_count = db.get_log_counters(session)
            return {
                "fsm_errors": error_count,
                "fsm_actions": fsm_count,
                "hardware_commands": hw_count
            }
        except DbLayerError as e:
            raise HTTPException(status_code=400, detail=str(e))
