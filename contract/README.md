# Platform Integration Contract — Domain adapter

Thin Domain adapter for
[`specs/platform-integration-contract.md`](../specs/platform-integration-contract.md).

| Module | Role |
|--------|------|
| `mapping.py` | Public Operation → enqueue/REST (internal only) |
| `adapter.py` | `DomainIntegrationAdapter` implementing the contract |

## Status

Work in progress. `perform` and entity-level `observe` still need wiring to
`DatabaseLayer.enqueue_fsm_instance`, the order-request pipeline, and SSE.

Do not expose raw `fsm_action` / `process_name` to PI or Scenario Runner.

## Planned follow-ups

1. Wire `CREATE_ORDER`, `ASSIGN_COURIER`, `OPEN_CELL` end-to-end.
2. Entity-level SSE `ChangeEvent` stream.
3. REST façade `/api/contract/*` if PI needs HTTP rather than in-process calls.
4. Scenario Runner (separate repository) consuming this contract and the Scenario Language summarized in `specs/scenario-language.md`.
