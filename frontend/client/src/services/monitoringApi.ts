// Defines the structure for API calls related to database monitoring data.

import { LockInfo, ActivityPoint, DbObjectInfo } from '../types/monitoring'; // Import from shared types file

// Base URL for your backend API - adjust if necessary
const API_BASE_URL = '/api/v1/monitoring';

/**
 * Converts a simple time range string (e.g., "1h", "6h", "24h", "7d")
 * into start and end Date objects.
 * @param timeRange - The simple time range string.
 * @returns An object containing { startTime: Date, endTime: Date }.
 */
const convertTimeRangeToDates = (timeRange: string): { startTime: Date, endTime: Date } => {
  const now = new Date();
  let startTime = new Date(now);
  const endTime = new Date(now); // End time is always 'now'

  switch (timeRange) {
    case '1h':
      startTime.setHours(now.getHours() - 1);
      break;
    case '6h':
      startTime.setHours(now.getHours() - 6);
      break;
    case '24h':
      startTime.setDate(now.getDate() - 1);
      break;
    case '7d':
      startTime.setDate(now.getDate() - 7);
      break;
    // Add more cases if needed
    default:
      // Default to 1 hour if range is unknown
      startTime.setHours(now.getHours() - 1);
      break;
  }

  return { startTime, endTime };
};

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
 * @param timeRange - Optional: Specify the time range (e.g., '1h', '6h', '24h', '7d'). Backend default if omitted.
 * @returns A promise that resolves to an array of ActivityPoint objects.
 */
export const getActivity = async (db_id: string, timeRange?: string): Promise<ActivityPoint[]> => {
  // Construct the URL
  let url = `${API_BASE_URL}/activity/timeseries/${db_id}`; // Correct endpoint path

  if (timeRange) {
    // Convert the simple time range string to Date objects
    const { startTime, endTime } = convertTimeRangeToDates(timeRange);

    // Format dates as ISO strings for the backend query parameters
    const params = new URLSearchParams({
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString(),
    });
    url += `?${params.toString()}`;
  }
  // If no timeRange is provided, the backend will use its default range.

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

  const responseData = await response.json();
  // Extract the actual array from the response object
  if (!responseData || !Array.isArray(responseData.data)) {
      console.error("Invalid response structure received from activity API:", responseData);
      throw new Error("Invalid data structure received from server.");
  }
  // Ensure the nested array conforms to ActivityPoint[] structure
  // Note: Backend returns { timestamp: datetime, count: int } in ActivityDataPoint.
  // Frontend ActivityPoint expects { timestamp: string, active_sessions: number, etc. }
  // We need to adapt the frontend type or backend response. For now, casting.
  return responseData.data as ActivityPoint[];
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