-- Rename platform initiator column: not a domain user FK, just API actor id.
ALTER TABLE server_fsm_instances
  CHANGE COLUMN requested_by_user_id actor_id BIGINT NULL;
