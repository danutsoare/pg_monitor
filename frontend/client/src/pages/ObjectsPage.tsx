import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Alert, Typography, Input, Tag, Modal, Spin, Descriptions, List, Card, Empty } from 'antd';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { getDbObjects, getDbObjectDetails } from '../services/monitoringApi';
import { DbObjectInfo, ObjectFullDetails, ColumnDetail, IndexDetail, ConstraintDetail } from '../types/monitoring';

const { Title, Text, Paragraph } = Typography;
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

  // State for object details modal
  const [selectedObjectForDetails, setSelectedObjectForDetails] = useState<DbObjectInfo | null>(null);
  const [objectDetails, setObjectDetails] = useState<ObjectFullDetails | null>(null);
  const [isDetailsModalVisible, setIsDetailsModalVisible] = useState<boolean>(false);
  const [detailsLoading, setDetailsLoading] = useState<boolean>(false);
  const [detailsError, setDetailsError] = useState<string | null>(null);

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

  // Fetch details when an object is selected
  useEffect(() => {
    if (selectedObjectForDetails && db_id) {
      const fetchDetails = async () => {
        setDetailsLoading(true);
        setDetailsError(null);
        setObjectDetails(null);
        try {
          const details = await getDbObjectDetails(
            db_id,
            selectedObjectForDetails.schema_name,
            selectedObjectForDetails.object_name,
            selectedObjectForDetails.object_type,
            selectedObjectForDetails.owner
          );
          setObjectDetails(details);
        } catch (err) {
          setDetailsError(err instanceof Error ? err.message : 'Failed to fetch object details.');
          console.error("Error fetching object details:", err);
        } finally {
          setDetailsLoading(false);
        }
      };
      fetchDetails();
    }
  }, [selectedObjectForDetails, db_id]);

  const handleRowClick = (record: DbObjectInfo) => {
    setSelectedObjectForDetails(record);
    setIsDetailsModalVisible(true);
  };

  const handleCloseDetailsModal = () => {
    setIsDetailsModalVisible(false);
    setSelectedObjectForDetails(null); // Clear selection
    setObjectDetails(null); // Clear details
    setDetailsError(null); // Clear error
  };

  // Memoized filtering logic - THIS WAS IMPORTANT AND SHOULD BE PRESERVED
  const filteredObjects = useMemo(() => {
    if (!searchText) {
      return objects;
    }
    const lowerSearchText = searchText.toLowerCase();
    return objects.filter((obj: DbObjectInfo) =>
      obj.schema_name.toLowerCase().includes(lowerSearchText) ||
      obj.object_name.toLowerCase().includes(lowerSearchText) ||
      obj.object_type.toLowerCase().includes(lowerSearchText) ||
      (obj.owner && obj.owner.toLowerCase().includes(lowerSearchText)) // Added check for obj.owner existing
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
      onFilter: (value: React.Key | boolean, record: DbObjectInfo) => record.object_type === (value as string),
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
    onRow: (record: DbObjectInfo) => {
      return {
        onClick: () => handleRowClick(record),
      };
    },
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

      {selectedObjectForDetails && (
        <Modal
          title={`Details for ${selectedObjectForDetails.object_type}: ${selectedObjectForDetails.schema_name}.${selectedObjectForDetails.object_name}`}
          visible={isDetailsModalVisible}
          onCancel={handleCloseDetailsModal}
          footer={null} // No OK/Cancel buttons, just informational
          width={900} // Wider modal for more content
          destroyOnClose // Reset state when modal is closed
        >
          {detailsLoading && <Spin tip="Loading details..." />}
          {detailsError && <Alert message="Error" description={detailsError} type="error" showIcon />}
          {objectDetails && !detailsLoading && (
            <div>
              <Descriptions bordered column={2} size="small">
                <Descriptions.Item label="Schema">{objectDetails.schema_name}</Descriptions.Item>
                <Descriptions.Item label="Name">{objectDetails.object_name}</Descriptions.Item>
                <Descriptions.Item label="Type">{objectDetails.object_type}</Descriptions.Item>
                <Descriptions.Item label="Owner">{objectDetails.owner ?? '-'}</Descriptions.Item>
                {objectDetails.row_count !== null && objectDetails.row_count !== undefined && (
                  <Descriptions.Item label="Row Count">{objectDetails.row_count.toLocaleString()}</Descriptions.Item>
                )}
                {objectDetails.access_method && (
                  <Descriptions.Item label="Access Method">{objectDetails.access_method}</Descriptions.Item>
                )}
                {objectDetails.options && objectDetails.options.length > 0 && (
                    <Descriptions.Item label="Options" span={2}>{objectDetails.options.join(', ')}</Descriptions.Item>
                )}
              </Descriptions>

              {objectDetails.view_definition && (
                <Card title="View Definition" style={{ marginTop: 16 }} size="small">
                  <Paragraph code copyable style={{ whiteSpace: 'pre-wrap' }}>{objectDetails.view_definition}</Paragraph>
                </Card>
              )}

              {objectDetails.columns && objectDetails.columns.length > 0 && (
                <Card title="Columns" style={{ marginTop: 16 }} size="small">
                  <Table<ColumnDetail>
                    dataSource={objectDetails.columns}
                    columns={[
                      { title: 'Name', dataIndex: 'column_name', key: 'column_name', sorter: (a: ColumnDetail, b: ColumnDetail) => a.column_name.localeCompare(b.column_name) },
                      { title: 'Type', dataIndex: 'data_type', key: 'data_type' },
                      { title: 'Nullable', dataIndex: 'is_nullable', key: 'is_nullable', render: (val: boolean) => (val ? 'Yes' : 'No') },
                      { title: 'Default', dataIndex: 'column_default', key: 'column_default', render: (val?: string | null) => val ?? '-' },
                      { title: 'Collation', dataIndex: 'collation', key: 'collation', render: (val?: string | null) => val ?? '-' },
                      { title: 'Description', dataIndex: 'description', key: 'description', render: (val?: string | null) => val ?? '-' },
                      // Add Storage, Compression, Stats Target if available and desired
                    ]}
                    rowKey="column_name"
                    pagination={{ pageSize: 5, size: 'small' }}
                    size="small"
                    scroll={{ x: 'max-content' }}
                  />
                </Card>
              )}

              {objectDetails.indexes && objectDetails.indexes.length > 0 && (
                 <Card title="Indexes" style={{ marginTop: 16 }} size="small">
                  <List<IndexDetail>
                    itemLayout="vertical"
                    dataSource={objectDetails.indexes}
                    renderItem={(item: IndexDetail) => (
                      <List.Item key={item.index_name}>
                        <List.Item.Meta
                          title={<Text strong>{item.index_name} ({item.index_type.toUpperCase()})</Text>}
                          description={item.is_primary_key ? <Tag color="gold">PRIMARY KEY</Tag> : item.is_unique ? <Tag color="purple">UNIQUE</Tag> : null}
                        />
                        <Paragraph code copyable style={{ whiteSpace: 'pre-wrap', fontSize: 'small' }}>
                          {item.index_definition}
                        </Paragraph>
                      </List.Item>
                    )}
                    pagination={{ pageSize: 3, size: 'small' }}
                  />
                </Card>
              )}

              {objectDetails.constraints && objectDetails.constraints.length > 0 && (
                <Card title="Constraints" style={{ marginTop: 16 }} size="small">
                  <List<ConstraintDetail>
                    dataSource={objectDetails.constraints}
                    renderItem={(item: ConstraintDetail) => (
                      <List.Item key={item.constraint_name}>
                        <List.Item.Meta
                          title={<Text strong>{item.constraint_name} ({item.constraint_type})</Text>}
                        />
                        <Paragraph code copyable style={{ whiteSpace: 'pre-wrap', fontSize: 'small' }}>
                            {item.definition}
                        </Paragraph>
                      </List.Item>
                    )}
                    pagination={{ pageSize: 3, size: 'small' }}
                  />
                </Card>
              )}
              
              {/* Show a message if no specific details are available for the object type (e.g. sequence) */}
              {!(objectDetails.columns && objectDetails.columns.length > 0) &&
               !(objectDetails.indexes && objectDetails.indexes.length > 0) && 
               !(objectDetails.constraints && objectDetails.constraints.length > 0) &&
               !objectDetails.view_definition &&
               objectDetails.object_type !== 'table' && // Tables might be empty but are valid
               objectDetails.object_type !== 'view' && // Views might be empty but are valid
               objectDetails.object_type !== 'materialized view' &&
                <Empty description={`No specific details to display for ${objectDetails.object_type}.`} style={{marginTop: 16}}/>
              }

            </div>
          )}
        </Modal>
      )}
    </div>
  );
};

export default ObjectsPage; 