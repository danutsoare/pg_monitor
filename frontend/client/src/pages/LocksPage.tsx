import React, { useState, useEffect } from 'react';
import { Table, Spin, Alert, Typography } from 'antd';
import { useParams } from 'react-router-dom'; // Assuming routing provides db_id
import { getLocks } from '../services/monitoringApi'; // Import specific function
import { LockInfo } from '../types/monitoring'; // Import shared type

const { Title } = Typography;
// const { Option } = Select; // Removed unused Option

// REMOVE local definition of LockInfo
// interface LockInfo {
//   pid: number;
//   relation: string;
//   locktype: string;
//   mode: string;
//   granted: boolean;
//   waitstart: string | null;
//   query: string;
// }

const LocksPage: React.FC = () => {
  const { db_id } = useParams<{ db_id: string }>(); // Get db_id from URL
  const [locks, setLocks] = useState<LockInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLocks = async () => {
      if (!db_id) {
        setError("Database ID not found in URL.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        // Use the imported getLocks function
        const data = await getLocks(db_id);
        setLocks(data || []); // Ensure data is an array
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch lock information.');
        console.error("Error fetching locks:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchLocks();
    // TODO: Implement refresh mechanism (e.g., setInterval or manual refresh button)
  }, [db_id]); // Refetch if db_id changes

  const columns = [
    { title: 'PID', dataIndex: 'pid', key: 'pid', sorter: (a: LockInfo, b: LockInfo) => a.pid - b.pid },
    { title: 'Relation', dataIndex: 'relation', key: 'relation', sorter: (a: LockInfo, b: LockInfo) => a.relation.localeCompare(b.relation) },
    { title: 'Lock Type', dataIndex: 'locktype', key: 'locktype' },
    { title: 'Mode', dataIndex: 'mode', key: 'mode' },
    { title: 'Granted', dataIndex: 'granted', key: 'granted', render: (granted: boolean) => (granted ? 'Yes' : 'No') },
    { title: 'Waiting Since', dataIndex: 'waitstart', key: 'waitstart', render: (ts?: string | null) => ts ? new Date(ts).toLocaleString() : '-' }, // Make ts optional to match interface
    { title: 'Blocked Query', dataIndex: 'query', key: 'query', ellipsis: true }, // Make query optional to match interface
    // Add more columns as needed based on pg_locks and backend data
  ];

  if (!db_id) {
    // Handle case where db_id is missing, maybe show a selection dropdown or message
     // For now, just showing an error message. A database selection mechanism is needed.
     return <Alert message="Error" description="No database selected. Please select a database from the main navigation or connections page." type="error" showIcon />;
  }


  return (
    <div>
      <Title level={2}>Locks & Blocking Information (DB ID: {db_id})</Title>
      {/* TODO: Add refresh button */}
      {error && <Alert message="Error fetching data" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}
      {loading ? (
        <Spin size="large" />
      ) : (
        <Table
          dataSource={locks}
          columns={columns}
          rowKey="pid" // Adjust if pid is not unique or use a composite key
          pagination={{ pageSize: 15 }}
          scroll={{ x: 1300 }} // Enable horizontal scroll if content is wide
          bordered
        />
      )}
    </div>
  );
};

export default LocksPage; 