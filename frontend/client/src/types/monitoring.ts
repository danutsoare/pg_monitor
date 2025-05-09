// Shared types for monitoring data

/**
 * Represents lock information obtained from the backend.
 * Matches the structure expected by LocksPage and returned by monitoringApi.getLocks.
 */
export interface LockInfo {
  pid: number;
  relation: string;      // Name of the relation being locked (if applicable)
  locktype: string;      // Type of lock (e.g., relation, transactionid, tuple)
  mode: string;          // Lock mode (e.g., AccessShareLock, RowExclusiveLock)
  granted: boolean;      // Whether the lock is currently held
  waitstart?: string | null; // Timestamp when the session started waiting (ISO string), null if not waiting
  query?: string;         // The query being executed by the process holding or waiting for the lock
  // Add other relevant fields from pg_locks or the backend API as needed
}

/**
 * Represents a single data point for database activity over time.
 */
export interface ActivityPoint {
  timestamp: string; // ISO timestamp string
  active_sessions: number;
  idle_sessions: number;
  waiting_sessions: number;
  // Add other relevant metrics like CPU usage, IO waits if available from backend
}

/**
 * Represents information about a database object (table, index, view, etc.).
 */
export interface DbObjectInfo {
  oid: number; // Object ID, potentially useful as a key
  schema_name: string;
  object_name: string;
  object_type: string; // e.g., 'table', 'index', 'view', 'sequence', 'materialized view'
  owner: string;
  size_bytes: number | null; // Size in bytes, might be null for some object types
  size_pretty: string | null; // Human-readable size (e.g., '1.2 MiB')
  // Add other relevant details like row count for tables if available
}

// --- Detailed Object Information Interfaces (matching backend Pydantic schemas) ---

export interface ColumnDetail {
  column_name: string;
  data_type: string;
  collation?: string | null;
  is_nullable: boolean;
  column_default?: string | null;
  storage?: string | null;
  compression?: string | null;
  stats_target?: number | null;
  description?: string | null;
}

export interface IndexDetail {
  index_name: string;
  index_definition: string;
  is_primary_key: boolean;
  is_unique: boolean;
  index_type: string;
}

export interface ConstraintDetail {
  constraint_name: string;
  constraint_type: string;
  definition: string;
}

export interface ObjectFullDetails {
  schema_name: string;
  object_name: string;
  object_type: string;
  owner?: string | null;
  columns?: ColumnDetail[] | null;
  row_count?: number | null;
  indexes?: IndexDetail[] | null;
  constraints?: ConstraintDetail[] | null;
  access_method?: string | null;
  options?: string[] | null; // Assuming reloptions are strings like "fillfactor=100"
  view_definition?: string | null;
  description?: string | null;
  // sequence_details?: any; // Define if sequence details are added later
}

// End of new interfaces

/**
 * Represents a single lock entry from pg_locks, potentially joined with pg_stat_activity.
 */
export interface LockEntry {
  // Add necessary fields to represent a lock entry
}

// Add other shared monitoring-related types here
// e.g., export interface ActivityInfo { ... }
// e.g., export interface StatementStat { ... } 