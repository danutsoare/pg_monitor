// Defines the structure for API calls related to database monitoring data.

import { LockInfo, ActivityPoint, DbObjectInfo } from '../types/monitoring'; // Import from shared types file

// Base URL for your backend API - adjust if necessary
const API_BASE_URL = '/api/monitoring';

/**
 * Fetches lock information for a specific database connection.
 * @param db_id - The ID of the database connection to monitor.
 * @returns A promise that resolves to an array of LockInfo objects.
 */
export const getLocks = async (db_id: string): Promise<LockInfo[]> => {
  const response = await fetch(`${API_BASE_URL}/${db_id}/locks`);

  if (!response.ok) {
    // Attempt to get more specific error info from response
    let errorMsg = 'Failed to fetch lock information';
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorMsg; // Assuming backend sends error details in 'detail' field
    } catch (e) {
      // Ignore if response body is not JSON or empty
    }
    console.error(`Error fetching locks for db ${db_id}: ${response.status} ${response.statusText}, Message: ${errorMsg}`);
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return data as LockInfo[]; // Assuming the API returns the data directly as an array
};

/**
 * Fetches time series activity data for a specific database connection.
 * @param db_id - The ID of the database connection to monitor.
 * @param timeRange - Optional: Specify the time range (e.g., '1h', '6h', '24h', '7d'). Defaults to a server-defined period.
 * @returns A promise that resolves to an array of ActivityPoint objects.
 */
export const getActivity = async (db_id: string, timeRange?: string): Promise<ActivityPoint[]> => {
  // Construct the URL, adding timeRange query parameter if provided
  let url = `${API_BASE_URL}/${db_id}/activity`;
  if (timeRange) {
    url += `?timeRange=${encodeURIComponent(timeRange)}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    let errorMsg = 'Failed to fetch activity data';
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorMsg;
    } catch (e) { /* Ignore */ }
    console.error(`Error fetching activity for db ${db_id}: ${response.status} ${response.statusText}, Message: ${errorMsg}`);
    throw new Error(errorMsg);
  }

  const data = await response.json();
  // Optional: Add data validation here if needed
  return data as ActivityPoint[];
};

/**
 * Fetches database object information for a specific database connection.
 * @param db_id - The ID of the database connection to monitor.
 * @returns A promise that resolves to an array of DbObjectInfo objects.
 */
export const getDbObjects = async (db_id: string): Promise<DbObjectInfo[]> => {
  const url = `${API_BASE_URL}/${db_id}/objects`;
  const response = await fetch(url);

  if (!response.ok) {
    let errorMsg = 'Failed to fetch database objects';
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorMsg;
    } catch (e) { /* Ignore */ }
    console.error(`Error fetching objects for db ${db_id}: ${response.status} ${response.statusText}, Message: ${errorMsg}`);
    throw new Error(errorMsg);
  }

  const data = await response.json();
  return data as DbObjectInfo[];
};

// Add other monitoring API functions here as needed, e.g.:
// export const getActivity = async (db_id: string) => { ... };
// export const getStatementStats = async (db_id: string) => { ... };
// export const getObjectSizes = async (db_id: string) => { ... }; 