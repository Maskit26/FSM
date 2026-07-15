# Scenario Language — pointer (this repository)

**Status:** Not implemented here. Used by Scenario Runner (separate Python repository).

## What this is

Scenario Language is a **declarative YAML DSL** for describing multi-actor business flows executed through the Platform Integration Contract.

It answers: *what should happen between actors?*  
It does not describe FSM internals, REST routes, or Core APIs.

## Relation to this repo

| Artifact | Role |
|----------|------|
| `specs/platform-integration-contract.md` | How any client (PI, Runner, …) talks to Domain |
| `specs/operations-catalog.md` | Public `perform.operation` names for this Domain |
| This file | Summary of the scenario DSL used **only by Scenario Runner** |

**Platform Interactive does not execute scenario YAML.**  
PI uses the Integration Contract directly (voice / Telegram / UI). Scenario files are for automated Runner runs (regression, contract checks, reproducing bugs).

## Language shape (summary)

* top-level: `version`, `scenario`, `sessions`, `actors`, `steps`
* step: `wait` → `perform` → `expect`
* `perform.operation` — public name from the Operations Catalog (e.g. `CREATE_ORDER`)
* `wait` / `expect` in MVP: `type: state`, `value: <Snapshot.state>`
* Object ids: Runner keeps refs from `OperationResult.objects` and passes them explicitly on later steps

Full normative text and JSON Schema will live in the Scenario Runner repository (for example `specs/scenario-language.md` and `schemas/scenario.schema.json`).

## First scenario to validate against this Domain

Happy path: **courier / courier** delivery, including the **recipient** as the last actor
(see also `operations-catalog.md`).

Illustrative skeleton (state strings must match Domain `Snapshot.state`;
`object` refs come from prior `OperationResult.objects` — omitted here for brevity):

```yaml
version: 1

scenario:
  id: delivery_courier_courier
  name: Successful courier-courier delivery
  timeout: 15m

sessions:
  client: {}
  courier1: {}
  driver: {}
  courier2: {}
  recipient: {}

actors:
  client:
    session: client
  courier1:
    session: courier1
  driver:
    session: driver
  courier2:
    session: courier2
  recipient:
    session: recipient

steps:
  - id: create
    actor: client
    perform:
      operation: CREATE_ORDER
      params:
        recipient_user_id: 200
        parcel_type: box
        cell_size: M
        sender_delivery: courier
        recipient_delivery: courier
    expect:
      type: state
      value: order_created   # replace with actual Snapshot.state after create

  - id: assign_pickup
    actor: courier1
    wait:
      type: state
      value: order_created
      timeout: 60s
    perform:
      operation: ASSIGN_COURIER
      params:
        target_user_id: 301
        leg: pickup

  # … courier1 pickup / cells, driver trip / loading, courier2 assign …

  - id: confirm_courier2_delivery
    actor: courier2
    wait:
      type: state
      value: order_courier2_has_parcel
      timeout: 60s
    perform:
      operation: CONFIRM_COURIER2_DELIVERY
    expect:
      type: state
      value: order_courier2_parcel_delivered

  - id: recipient_confirm
    actor: recipient
    wait:
      type: state
      value: order_courier2_parcel_delivered
      timeout: 60s
    perform:
      operation: CONFIRM_PICKUP
    expect:
      type: state
      value: order_completed
```

`CONFIRM_PICKUP` is the recipient’s closing step (UI today: `confirm_pickup`).
If it is missing from `operations-catalog.md`, add it there before Runner uses this scenario.
