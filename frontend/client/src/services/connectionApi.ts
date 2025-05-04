// Define the Connection interface matching the form and list components
export interface Connection {
    id?: number;
    name: string;
    host: string;
    port: number;
    user: string;
    dbname: string;
    password?: string;
  }

  // Base URL for your backend API
  const API_BASE_URL = '/api/v1'; // Adjust if your backend is hosted elsewhere or has a prefix

  // Function to get all connections
  export const getConnections = async (): Promise<Connection[]> => {
    const response = await fetch(`${API_BASE_URL}/connections`);
    if (!response.ok) {
      throw new Error('Failed to fetch connections');
    }
    return response.json();
  };

  // Function to add a new connection
  export const addConnection = async (connection: Connection): Promise<Connection> => {
    const response = await fetch(`${API_BASE_URL}/connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connection),
    });
    if (!response.ok) {
      // Consider more specific error handling based on response status/body
      throw new Error('Failed to add connection');
    }
    return response.json();
  };

  // Function to update an existing connection
  export const updateConnection = async (id: number, connection: Connection): Promise<Connection> => {
    const response = await fetch(`${API_BASE_URL}/connections/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connection),
    });
    if (!response.ok) {
      throw new Error('Failed to update connection');
    }
    return response.json();
  };

  // Function to delete a connection
  export const deleteConnection = async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/connections/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete connection');
    }
    // No content expected on successful delete
  }; 