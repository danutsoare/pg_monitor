import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Spin, Alert, Typography, Input, Tag } from 'antd';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { getDbObjects } from '../services/monitoringApi';
import { DbObjectInfo } from '../types/monitoring';

const { Title } = Typography;
const { Search } = Input;

// Helper function to determine tag color based on object type
const getObjectTypeColor = (type: string): string => {
  switch (type) {
    case 'table': return 'blue';
    case 'index': return 'green';
    case 'view': return 'purple';
    case 'sequence': return 'orange';
    case 'materialized view': return 'cyan';
    case 'foreign table': return 'geekblue';
    default: return 'default';
  }
};

const ObjectsPage: React.FC = () => {
  const { db_id } = useParams<{ db_id: string }>();
  const [objects, setObjects] = useState<DbObjectInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState<string>('');

  useEffect(() => {
    const fetchObjects = async () => {
      if (!db_id) {
        setError("Database ID not found in URL.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await getDbObjects(db_id);
        setObjects(data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch object information.');
        console.error("Error fetching objects:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchObjects();
  }, [db_id]);

  // Memoized filtering logic
  const filteredObjects = useMemo(() => {
    if (!searchText) {
      return objects;
    }
    const lowerSearchText = searchText.toLowerCase();
    return objects.filter((obj: DbObjectInfo) =>
      obj.schema_name.toLowerCase().includes(lowerSearchText) ||
      obj.object_name.toLowerCase().includes(lowerSearchText) ||
      obj.object_type.toLowerCase().includes(lowerSearchText) ||
      obj.owner.toLowerCase().includes(lowerSearchText)
    );
  }, [objects, searchText]);

  const columns: ColumnsType<DbObjectInfo> = [
    {
      title: 'Schema',
      dataIndex: 'schema_name',
      key: 'schema',
      sorter: (a: DbObjectInfo, b: DbObjectInfo) => a.schema_name.localeCompare(b.schema_name),
      width: 150,
    },
    {
      title: 'Name',
      dataIndex: 'object_name',
      key: 'name',
      sorter: (a: DbObjectInfo, b: DbObjectInfo) => a.object_name.localeCompare(b.object_name),
    },
    {
      title: 'Type',
      dataIndex: 'object_type',
      key: 'type',
      render: (type: string) => (
        <Tag color={getObjectTypeColor(type)} key={type}>
          {type.toUpperCase()}
        </Tag>
      ),
      sorter: (a: DbObjectInfo, b: DbObjectInfo) => a.object_type.localeCompare(b.object_type),
      filters: useMemo(() => {
          const types = [...new Set(objects.map((obj: DbObjectInfo) => obj.object_type))];
          return types.map((type: string) => ({ text: type, value: type }));
      }, [objects]),
      onFilter: (value: string | number | boolean, record: DbObjectInfo) => record.object_type === value,
      width: 180,
    },
    {
      title: 'Owner',
      dataIndex: 'owner',
      key: 'owner',
      sorter: (a: DbObjectInfo, b: DbObjectInfo) => a.owner.localeCompare(b.owner),
      width: 150,
    },
    {
      title: 'Size',
      dataIndex: 'size_pretty',
      key: 'size',
      sorter: (a: DbObjectInfo, b: DbObjectInfo) => (a.size_bytes ?? -1) - (b.size_bytes ?? -1),
      render: (size: string | null) => size ?? '-',
      width: 120,
      align: 'right',
    },
    // Add more columns if needed (e.g., oid)
  ];

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  // Type assertion for Table props due to filter typing issues with Ant Design < 5.x
  // In newer versions, this might not be necessary or might need adjustment.
  const tableProps: TableProps<DbObjectInfo> = {
    columns,
    dataSource: filteredObjects,
    loading,
    rowKey: 'oid', // Use oid as the key
    pagination: { pageSize: 20, showSizeChanger: true, pageSizeOptions: ['10', '20', '50', '100'] },
    scroll: { y: 'calc(100vh - 300px)' }, // Adjust scroll height based on layout
    bordered: true,
    size: 'small',
  };

  if (!db_id) {
     return <Alert message="Error" description="No database selected. Please select a database first." type="error" showIcon />;
  }

  return (
    <div>
      <Title level={2}>Object Browser (DB ID: {db_id})</Title>
      <Search
        placeholder="Filter by schema, name, type, or owner..."
        onSearch={handleSearch} // Trigger search on enter
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleSearch(e.target.value)} // Trigger search as you type; Add event type
        style={{ marginBottom: 16, width: '40%' }}
        allowClear
        enterButton
      />

      {error && <Alert message="Error fetching data" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      <Table {...tableProps} />

    </div>
  );
};

export default ObjectsPage; 