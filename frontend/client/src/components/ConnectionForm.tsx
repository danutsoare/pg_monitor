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
    // Antd form passes all values

    // Explicitly check password, backend requires a non-empty string for create
    if (!values.password || !values.password.trim()) {
        // This should ideally be caught by form validation, but double-check
        console.error("Password cannot be empty.");
        // Optionally: form.setFields([{ name: 'password', errors: ['Password is required!'] }]);
        return; // Prevent submission
    }

    const connectionData: Connection = {
      id: initialData?.id,
      alias: values.alias,
      hostname: values.hostname,
      port: values.port, // InputNumber should provide a number
      username: values.username,
      db_name: values.db_name,
      // Ensure password is a string, not undefined (it passed the check above)
      password: values.password,
    };

    try {
        await onSave(connectionData);
        form.resetFields(); // Reset form only on successful save
    } catch (error) {
        console.error("Error saving connection:", error);
        // Error handling (e.g., messageApi.error) is likely in the parent component's onSave
        // Keep the form populated so the user doesn't lose input
    }
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
        name="alias"
        label="Connection Name"
        rules={[{ required: true, message: 'Please input a name for the connection!' }]}
      >
        <Input placeholder="e.g., Production DB" />
      </Form.Item>

      <Form.Item
        name="hostname"
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
        name="username"
        label="Username"
        rules={[{ required: true, message: 'Please input the database username!' }]}
      >
        <Input placeholder="e.g., postgres" />
      </Form.Item>

      <Form.Item
        name="db_name"
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