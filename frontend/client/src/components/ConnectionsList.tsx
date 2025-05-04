import React from 'react';
import { Table, Button, Space, Popconfirm } from 'antd';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Connection } from '../services/connectionApi'; // Import the Connection type

interface ConnectionsListProps {
  connections: Connection[];
  onEdit: (connection: Connection) => void;
  onDelete: (id: number) => void;
}

const ConnectionsList: React.FC<ConnectionsListProps> = ({ connections, onEdit, onDelete }) => {

  const columns: ColumnsType<Connection> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Host',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'Port',
      dataIndex: 'port',
      key: 'port',
    },
    {
      title: 'User',
      dataIndex: 'user',
      key: 'user',
    },
    {
      title: 'Database',
      dataIndex: 'dbname',
      key: 'dbname',
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            icon={<EditOutlined />}
            onClick={() => onEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete the connection"
            description="Are you sure you want to delete this connection?"
            onConfirm={() => record.id && onDelete(record.id)} // Ensure id exists before calling onDelete
            okText="Yes"
            cancelText="No"
          >
            <Button icon={<DeleteOutlined />} danger>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
        columns={columns}
        dataSource={connections}
        rowKey="id" // Use the connection id as the unique key for each row
        pagination={{ pageSize: 10 }} // Optional: Add pagination
    />
  );
};

export default ConnectionsList; 