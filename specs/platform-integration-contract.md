# Platform Integration Contract Specification v1.0

**Status:** Normative Specification  
**Consumers:** Platform Interactive (PI), Scenario Runner (SR), Web UI, and any other Domain client

---

## 1. Purpose

This document defines the **minimum set of operations** any client needs to interact with the Domain System.

It does **not** define:

* transport implementation details beyond the required observe semantics for MVP;
* internal FSM architecture;
* SQL, stored procedures, or worker internals;
* Aristotel Core HTTP API.

Clients (PI and SR equally) talk **only** to this contract.

---

## 2. Normative design rules

| Topic | Rule |
|-------|------|
| Placement | Thin layer over the existing Domain API; same contract for PI and SR |
| Operations | Public names (`CREATE_ORDER`, `OPEN_CELL`, …) with internal mapping |
| `perform()` | Returns `OperationResult` (accepted / rejected) only |
| State after perform | Client obtains via `snapshot()` / `observe()` |
| Object model | Polymorphic: `order` \| `trip` \| `locker` \| `driver_reservation` \| `direction` \| `user` |
| `availableActions()` | Executable operations + params schema |
| `observe()` (MVP) | SSE with full change events (result, errors, what changed) |
| Core (Aristotel) | Not called by clients; exposed as Domain Operations (`LOGIN`, `CREATE_USER`, `CREATE_CAR`, …) |
| Object identity | `OperationResult.objects` returns created/affected refs; client passes `ObjectRef` explicitly on later calls |
| Scenario language | Declared in `specs/scenario-language.md`; executed by Scenario Runner (separate repository) |

---

## 3. Terms

### Client

Any system that uses this contract: Platform Interactive, Scenario Runner, Web UI, bots.

### Domain System

The parcel / postamat logistics backend (this repository) including its FSM and Core adapter.

### Session

Per-actor interaction context with the Domain System. Obtained via `LOGIN` (or equivalent session-establishing operation). Carries local user identity and any Core credentials required by Domain implementations. Clients never manage Core tokens themselves.

### Operation

A public client intention. Not an FSM transition name and not a worker `process_name`.

### ObjectRef

Polymorphic reference to a domain object:

```text
{ "type": "order" | "trip" | "locker" | "driver_reservation" | "direction" | "user",
  "id": <int> }
```

### Snapshot

Read-only model of an object for display and expectation checks. Mutations happen only via Operations.

### OperationResult

Acceptance/rejection of an Operation. Does **not** embed business state. May include **created / affected object refs** for the client to reuse explicitly.

---

## 4. Contract surface

Every conforming implementation MUST provide:

| Method | Responsibility |
|--------|----------------|
| `perform(session, operation, params, object?)` | Execute an Operation |
| `snapshot(session, object)` | Return current Snapshot |
| `availableActions(session, object)` | Return executable actions + params schema |
| `observe(session, object \| job)` | Stream change events (SSE for MVP) |

Optional but recommended for clients:

| Method | Responsibility |
|--------|----------------|
| `login(credentials) → Session` | Establish Session (maps to Domain `LOGIN`) |
| `logout(session)` | Invalidate Session |

`login` / `logout` MAY be modeled as Operations (`LOGIN`, `LOGOUT`) invoked through `perform` with a null/anonymous session bootstrap. Implementations MUST document which approach they use. This repository uses dedicated session helpers plus the same Session type everywhere.

---

## 5. `perform`

### Input

| Field | Required | Description |
|-------|----------|-------------|
| `session` | yes | Active Session |
| `operation` | yes | Public operation name |
| `params` | no | Opaque dictionary interpreted only by Domain |
| `object` | conditional | `ObjectRef` of the target; required when the operation acts on an existing object |

### Output — `OperationResult`

```text
accepted: bool
operation: string
error_code?: string          # CONTRACT_* or DOMAIN_*
error_message?: string
job_id?: string | int        # present when execution is async
objects?: ObjectRef[]        # created and/or primarily affected objects
correlation_id?: string
```

Rules:

1. `accepted == true` means Domain **accepted** the intention, not that the business process finished.
2. Final business state is obtained only via `snapshot` / `observe`.
3. If the Domain creates objects (e.g. `CREATE_ORDER`), `objects` MUST list them so the client can pass `object_id` on later calls.
4. Async work MAY set `job_id`; client MAY observe that job and/or the affected objects.

---

## 6. `snapshot`

### Input

| Field | Required |
|-------|----------|
| `session` | yes |
| `object` | yes (`ObjectRef`) |

### Output — `Snapshot`

Contract does **not** freeze a single JSON schema per type, but every Snapshot MUST allow a client to determine at least:

* `object` — ObjectRef;
* `state` — current business state string;
* `participants` — actors related to the object (ids + roles as available);
* `related` — related ObjectRefs (cells, trips, reservations, …);
* `data` — domain-specific fields;
* `updated_at` — last known change timestamp when available.

Domain MAY add fields freely. Clients MUST treat unknown fields as opaque.

---

## 7. `availableActions`

### Input

| Field | Required |
|-------|----------|
| `session` | yes |
| `object` | yes |

### Output — `AvailableActions`

List of descriptors:

```text
operation: string              # public name, executable via perform()
label?: string                 # optional UI label
enabled: bool
reason_disabled?: string
params_schema: object          # JSON Schema (draft 2020-12 subset) for perform.params
requires_object: bool          # usually true
```

Rules:

1. Clients NEVER compute allowed actions from FSM tables.
2. Returned `operation` values are the **only** names clients may pass to `perform` for that object/session.
3. `params_schema` MUST describe required/optional params (`leg`, `target_user_id`, …). For human PI flows, `pin` MAY appear when the user enters it; Domain MAY also resolve PIN internally for automated clients.

---

## 8. `observe`

### MVP transport

**Server-Sent Events (SSE)** delivering full change events.

Clients MAY additionally poll `snapshot` (Scenario Runner Wait uses polling or SSE equivalently).

### Subscription targets

* an `ObjectRef` — entity lifecycle / state changes;
* a `job_id` — async operation completion.

### Event payload (`ChangeEvent`)

```text
event_id: string
timestamp: string              # ISO-8601
source: "operation" | "system" | "job"
object?: ObjectRef
job_id?: string | int
operation?: string
accepted?: bool
state?: string                 # new state when known
snapshot?: Snapshot            # optional embedded snapshot
error_code?: string
error_message?: string
message?: string
```

PI uses these events to refresh UI/voice/chat and to show success/failure. SR uses them (or polled snapshots) for Wait/Expect.

---

## 9. Session

* Independent Sessions per actor are mandatory (client, courier, operator, driver, …).
* Auth mechanism is Domain-owned. MVP establishes Session via Domain login (Core-backed).
* Contract does not prescribe token format; adapter implementations define how Session is passed (header, cookie, opaque handle).

---

## 10. Errors

### Contract Error

Violation of the contract itself, e.g.:

* missing / invalid Session;
* unknown Operation;
* malformed params vs `params_schema`;
* missing required `object`.

Codes SHOULD use prefix `CONTRACT_`.

### Domain Error

Business rejection, e.g.:

* transition not allowed;
* access denied;
* object not found;
* Core dependency failed.

Codes SHOULD use prefix `DOMAIN_`. Content is Domain-defined.

`perform` returns Domain errors with `accepted: false`. Transport/protocol failures are distinct from both and handled by the client HTTP/SSE layer.

---

## 11. Object identity

1. Client does **not** rely on an implicit “current object” stored only in Session.
2. After `CREATE_*` (or any creating operation), client reads `OperationResult.objects`.
3. Subsequent `perform` / `snapshot` / `availableActions` / `observe` pass that `ObjectRef` explicitly.
4. Scenario Runner stores refs in its own execution context. Scenario Language may define capture syntax for those refs; that does not change this contract.

---

## 12. Core (Aristotel)

* Clients MUST NOT call Core HTTP APIs for Domain workflows.
* Capabilities that exist only in Core (`CREATE_USER`, `CREATE_CAR`, `LOGIN`, verification, …) MUST be available as Operations (or session helpers) on this contract.
* Domain adapter invokes Core internally and maps results into `OperationResult` / Snapshot fields.

---

## 13. Compatibility

Changes to FSM tables, worker processes, or Core endpoints MUST NOT change this contract’s method signatures or public Operation names. New Operations MAY be added. Deprecated Operations MUST remain until clients migrate.

---

## 14. Repository layout

```text
specs/platform-integration-contract.md   # this document
specs/operations-catalog.md              # public operations + internal mapping notes
specs/scenario-language.md               # pointer to Scenario Runner DSL
interfaces/IntegrationContract.py
interfaces/IntegrationContract.ts
contract/                                # thin Domain adapter
```

Scenario Runner lives in a **separate Python repository** and consumes this contract. The scenario YAML language is summarized in `specs/scenario-language.md`; the full Runner-side normative spec and JSON Schema belong in that repository.

---

## 15. Conformance

An implementation is conforming if PI and SR can:

1. establish Sessions per actor;
2. discover actions via `availableActions`;
3. execute via `perform` and receive `OperationResult` with object refs;
4. read state via `snapshot`;
5. receive change/error/completion information via `observe` (SSE).

Internal mapping to `/api/fsm/enqueue`, `/api/fsm/action`, entity GETs, and Core is an implementation detail of the Domain adapter.
