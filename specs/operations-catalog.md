# Operations Catalog v1.0 (Draft)

Public Operations for Platform Integration Contract.  
Internal mapping targets the Domain System in this repository.

Clients see **only** the Public name column.

---

## Legend

| Column | Meaning |
|--------|---------|
| Public | Name passed to `perform.operation` |
| Kind | `async` → enqueue + job_id; `sync` → immediate accept; `session` → session helper |
| Target object | Expected `ObjectRef.type` when acting on existing object |
| Internal | Current Domain mechanism (not part of the contract) |

Params listed are typical; authoritative shape comes from `availableActions[].params_schema` at runtime.

---

## Session & identity (Core-backed)

| Public | Kind | Target | Params (typical) | Internal |
|--------|------|--------|------------------|----------|
| `LOGIN` | session | — | `login`, `password`, `type?` | `POST /api/users/login` → Core auth |
| `LOGOUT` | session | — | — | `POST /api/users/logout` |
| `CREATE_USER` | sync | — | `name`, `phone`, `password`, `role_name`, `city`, `email?` | `POST /api/users/register` → Core |
| `CREATE_CAR` | sync | `user` | car attributes (`seats`, `custom_*`, …) | `POST /api/users/{id}/car/create` → Core |
| `VERIFY_USER` | sync | `user` | `u_check_state`, admin context via Session | `POST /api/users/verify-state` → Core |

---

## Orders

| Public | Kind | Target | Params (typical) | Internal |
|--------|------|--------|------------------|----------|
| `CREATE_ORDER` | async | — (creates `order`) | `recipient_user_id`, `parcel_type`, `cell_size`, `sender_delivery`, `recipient_delivery` | `POST /api/client/create_order_request` → process `order_creation` |
| `CANCEL_ORDER` | async | `order` | — | enqueue `cancel_order` |
| `ASSIGN_COURIER` | async | `order` | `target_user_id`, `leg` (`pickup` \| `delivery`) | enqueue `assign_executor` |
| `REMOVE_COURIER` | async | `order` | `leg` | enqueue `remove_executor` |
| `CONFIRM_COURIER2_DELIVERY` | async | `order` | delivery confirmation params | enqueue `confirm_courier2_delivery` |
| `CONFIRM_PICKUP` | sync | `order` | — | recipient confirms receipt: `order_recipient_confirmed` (UI: `confirm_pickup`) |
| `BIND_ORDER_TO_TRIP` | async | `order` | trip / direction refs as required | enqueue `bind_order_to_trip` |
| `REPORT_ERROR` | async | `order` \| `locker` \| `trip` | `error_type`, … | enqueue `report_error` |

`CREATE_ORDER` MUST return created `order` (and may return related refs) in `OperationResult.objects` once known. If creation is async, client observes `job_id` and/or waits until Snapshot exists, then uses the returned ObjectRef on later calls.

---

## Lockers / cells

Note: Domain historically uses `entity_type=locker` with **cell id**. Contract `locker` ObjectRef refers to that cell id unless a future `locker_unit` type is introduced.

| Public | Kind | Target | Params (typical) | Internal |
|--------|------|--------|------------------|----------|
| `OPEN_CELL` | async | `locker` | optional `pin` for human PI; Domain MAY resolve PIN for SR | enqueue `open_cell` |
| `CLOSE_CELL` | async | `locker` | — | enqueue `close_cell` |
| `REQUEST_LOCKER_ACCESS_CODE` | async | `order` \| `locker` | `leg?` | enqueue `request_locker_access_code` |
| `REPORT_LOCKER_ERROR` | async | `locker` | error metadata | enqueue `locker_error` / `report_error` |

---

## Trips & driver exchange

| Public | Kind | Target | Params (typical) | Internal |
|--------|------|--------|------------------|----------|
| `START_TRIP` | async | `trip` or direction context | — | enqueue `start_trip` |
| `ARRIVE_AT_DESTINATION` | async | `trip` | — | enqueue `arrive_at_destination` |
| `COMPLETE_TRIP` | async | `trip` | — | enqueue `complete_trip` |
| `CANCEL_TRIP` | async | `trip` | — | enqueue `cancel_trip` |
| `RESERVE_DIRECTION_SLOT` | async | `direction` | `capacity` | enqueue `direction_reserve_slot` |
| `START_LOADING` | async | `driver_reservation` | — | enqueue `driver_reservation_start_loading` |
| `COMPLETE_LOADING` | async | `direction` / reservation | — | enqueue `direction_complete_loading` |
| `CANCEL_RESERVATION` | async | `driver_reservation` | — | enqueue `driver_reservation_cancel` |

---

## Sync FSM escapes (restricted)

Low-level DB transitions (`POST /api/fsm/action`) are **not** exposed as a generic public Operation.

If a product need cannot be met by the catalog above, Domain adds a **named** public Operation and maps it internally. Emulator-only endpoints stay out of the contract.

---

## Mapping principles

1. UI `button_states.button_name` → Public Operation (adapter table).
2. Public Operation → `process_name` and/or specialized REST route.
3. `fsm_actions.action_name` stays inside Domain; never returned from `availableActions` as the executable id.
4. Adding a new worker process requires a catalog entry (or an explicit decision that it is internal-only, e.g. `locker_cleanup`).

### Internal-only processes (not public)

| process_name | Reason |
|--------------|--------|
| `locker_cleanup` | System maintenance |

---

## Happy-path reference (courier / courier)

Recommended first end-to-end path for Scenario Runner (see `scenario-language.md`):

1. Sessions: client, courier1, driver, courier2, **recipient** — each via `LOGIN`.
2. `CREATE_ORDER` with `sender_delivery=courier`, `recipient_delivery=courier` → take `order` from `OperationResult.objects` / observe.
3. `ASSIGN_COURIER` (leg `pickup`) → wait state.
4. Courier1 cell / parcel Operations → wait.
5. Driver reservation / trip Operations → wait.
6. `ASSIGN_COURIER` (leg `delivery`) → wait.
7. `CONFIRM_COURIER2_DELIVERY` → wait `order_courier2_parcel_delivered`.
8. Recipient `CONFIRM_PICKUP` → expect `order_completed`.

Exact state names remain Domain Snapshot values; Scenario Wait/Expect compare against Snapshot.state strings.

---

## Change policy

* New public Operations: additive, documented here.
* Rename of public Operations: forbidden without major contract version bump.
* Internal mapping changes: allowed anytime without client changes.
