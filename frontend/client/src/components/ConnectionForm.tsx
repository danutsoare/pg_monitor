import React, { useEffect } from 'react';
import { Form, Input, InputNumber, Button, Space } from 'antd';
import type { Connection } from '../services/connectionApi';

// TODO: Define props, likely including an optional connection object for editing
// and a function to handle form submission (onSave)
interface ConnectionFormProps {
  initialData?: Connection;
  onSave: (values: Connection) => Promise<void>; // Make async to handle API calls
  onCancel: () => void;
}

const ConnectionForm: React.FC<ConnectionFormProps> = ({ initialData, onSave, onCancel }) => {
  const [form] = Form.useForm();

  // Populate form fields when initialData changes (for editing)
  useEffect(() => {
    if (initialData) {
      form.setFieldsValue(initialData);
    } else {
      form.resetFields(); // Clear fields for adding new connection
    }
  }, [initialData, form]);

  const handleFinish = async (values: any) => {
    // Antd form passes all values, map them to Connection type expected by onSave
    // Assuming the form field names match the Connection interface keys
    const connectionData: Connection = {
      id: initialData?.id, // Include id if editing
      name: values.name,
      host: values.host,
      port: values.port,
      user: values.user,
      dbname: values.dbname,
      password: values.password || undefined, // Send undefined if empty, not empty string
    };
    await onSave(connectionData); // Let the parent handle success/error messaging and modal closing
    form.resetFields(); // Reset form after successful save
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      initialValues={{ port: 5432 }} // Set default port
      autoComplete="off"
    >
      <Form.Item
        name="name"
        label="Connection Name"
        rules={[{ required: true, message: 'Please input a name for the connection!' }]}
      >
        <Input placeholder="e.g., Production DB" />
      </Form.Item>

      <Form.Item
        name="host"
        label="Host"
        rules={[{ required: true, message: 'Please input the database host!' }]}
      >
        <Input placeholder="e.g., localhost or mydb.example.com" />
      </Form.Item>

      <Form.Item
        name="port"
        label="Port"
        rules={[
          { required: true, message: 'Please input the database port!' },
          { type: 'number', min: 1, max: 65535, message: 'Port must be between 1 and 65535'}
        ]}
      >
        <InputNumber style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item
        name="user"
        label="Username"
        rules={[{ required: true, message: 'Please input the database username!' }]}
      >
        <Input placeholder="e.g., postgres" />
      </Form.Item>

      <Form.Item
        name="dbname"
        label="Database Name"
        rules={[{ required: true, message: 'Please input the database name!' }]}
      >
        <Input placeholder="e.g., postgres" />
      </Form.Item>

      <Form.Item
        name="password"
        label="Password"
        rules={[{ required: !initialData, message: 'Password is required for new connections!' }]}
        help={initialData ? "Leave blank to keep the existing password" : undefined}
      >
        <Input.Password placeholder="Enter database password" />
      </Form.Item>

      <Form.Item style={{ textAlign: 'right' }}>
        <Space>
          <Button onClick={onCancel}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit">
            {initialData ? 'Save Changes' : 'Add Connection'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default ConnectionForm; 