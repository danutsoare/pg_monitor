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

// Add other shared monitoring-related types here
// e.g., export interface ActivityInfo { ... }
// e.g., export interface StatementStat { ... } 