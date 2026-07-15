/**
 * Platform Integration Contract — TypeScript interface (normative shapes).
 *
 * Primary consumer: Platform Interactive.
 * Scenario Runner uses the Python twin; both MUST stay semantically aligned.
 */

export type ObjectType =
  | "order"
  | "trip"
  | "locker"
  | "driver_reservation"
  | "direction"
  | "user";

export interface ObjectRef {
  type: ObjectType;
  id: number;
}

/** Opaque Domain session. Adapter defines wire format (header/token). */
export interface Session {
  sessionId: string;
  userId: number;
  role?: string;
  attributes?: Record<string, unknown>;
}

export interface OperationResult {
  accepted: boolean;
  operation: string;
  errorCode?: string;
  errorMessage?: string;
  jobId?: string | number;
  /** Created / affected objects for the client to pass explicitly on later calls */
  objects?: ObjectRef[];
  correlationId?: string;
}

export interface Snapshot {
  object: ObjectRef;
  state: string;
  participants?: Record<string, unknown>;
  related?: ObjectRef[];
  data?: Record<string, unknown>;
  updatedAt?: string;
}

/** JSON Schema (draft 2020-12 subset) describing perform.params */
export type ParamsSchema = Record<string, unknown>;

export interface ActionDescriptor {
  operation: string;
  enabled: boolean;
  paramsSchema: ParamsSchema;
  requiresObject?: boolean;
  label?: string;
  reasonDisabled?: string;
}

export interface ChangeEvent {
  eventId: string;
  timestamp: string;
  source: "operation" | "system" | "job" | string;
  object?: ObjectRef;
  jobId?: string | number;
  operation?: string;
  accepted?: boolean;
  state?: string;
  snapshot?: Snapshot;
  errorCode?: string;
  errorMessage?: string;
  message?: string;
}

export interface Credentials {
  login: string;
  password: string;
  type?: string;
}

export interface PerformRequest {
  session: Session;
  operation: string;
  params?: Record<string, unknown>;
  object?: ObjectRef;
}

export interface ObserveTarget {
  session: Session;
  object?: ObjectRef;
  jobId?: string | number;
}

/**
 * Normative contract surface. Same semantics for PI and Scenario Runner.
 */
export interface IntegrationContract {
  login(credentials: Credentials): Promise<Session>;

  logout(session: Session): Promise<void>;

  perform(request: PerformRequest): Promise<OperationResult>;

  snapshot(session: Session, object: ObjectRef): Promise<Snapshot>;

  availableActions(
    session: Session,
    object: ObjectRef
  ): Promise<ActionDescriptor[]>;

  /**
   * MVP: SSE stream of ChangeEvent.
   * Exactly one of object / jobId must be set on the target.
   */
  observe(target: ObserveTarget): AsyncIterable<ChangeEvent>;
}
