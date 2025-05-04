import React, { useState, useEffect } from 'react';
import { Button, Modal, Spin, Alert, message } from 'antd'; // Import Ant Design components
import ConnectionsList from '../components/ConnectionsList';
import ConnectionForm from '../components/ConnectionForm';
import { getConnections, addConnection, updateConnection, deleteConnection, Connection } from '../services/connectionApi';
// import type { Connection } from '../services/connectionApi'; // No longer need type-only import

const ConnectionManagementPage: React.FC = () => {
    const [connections, setConnections] = useState<Connection[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [editingConnection, setEditingConnection] = useState<Connection | null>(null);
    const [messageApi, contextHolder] = message.useMessage(); // For showing success/error messages

    // Fetch connections on mount
    const fetchConnections = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getConnections();
            setConnections(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
            messageApi.error('Failed to load connections.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []); // Empty dependency array means this runs once on mount

    // --- Modal Handlers ---
    const showAddModal = () => {
        setEditingConnection(null); // Ensure we are adding, not editing
        setIsModalOpen(true);
    };

    const showEditModal = (connection: Connection) => {
        setEditingConnection(connection);
        setIsModalOpen(true);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
        setEditingConnection(null);
    };

    // --- CRUD Handlers ---
    const handleSave = async (values: Connection) => {
        // `values` comes from the Ant Design form
        const connectionData = { ...values }; // id is added by backend on create
        const isEditing = !!editingConnection;

        try {
            if (isEditing && editingConnection?.id) {
                await updateConnection(editingConnection.id, connectionData);
                messageApi.success('Connection updated successfully!');
            } else {
                await addConnection(connectionData);
                messageApi.success('Connection added successfully!');
            }
            setIsModalOpen(false);
            setEditingConnection(null);
            fetchConnections(); // Refresh list
        } catch (err) {
            messageApi.error(`Failed to ${isEditing ? 'update' : 'add'} connection.`);
            console.error(err);
            // Keep modal open on error for user to retry/correct
        }
    };

    const handleDelete = async (id: number) => {
        // Optional: Add confirmation dialog here
        Modal.confirm({
            title: 'Are you sure you want to delete this connection?',
            content: 'This action cannot be undone.',
            okText: 'Yes, Delete',
            okType: 'danger',
            cancelText: 'No',
            onOk: async () => {
                try {
                    await deleteConnection(id);
                    messageApi.success('Connection deleted successfully!');
                    fetchConnections(); // Refresh list
                } catch (err) {
                    messageApi.error('Failed to delete connection.');
                    console.error(err);
                }
            },
        });
    };

    return (
        <div>
            {contextHolder} { /* Needed for message.useMessage() */}
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Connection Management</h1>
                <Button type="primary" onClick={showAddModal}>
                    Add New Connection
                </Button>
            </div>

            {isLoading && <Spin tip="Loading Connections..."><div style={{ height: '100px' }} /></Spin>}

            {error && !isLoading && <Alert message="Error" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}

            {!isLoading && !error && (
                <ConnectionsList
                    connections={connections}
                    onEdit={showEditModal} // Pass handler to list item
                    onDelete={handleDelete} // Pass handler to list item
                />
            )}

            <Modal
                title={editingConnection ? 'Edit Connection' : 'Add New Connection'}
                open={isModalOpen}
                onCancel={handleCancel}
                footer={null} // Footer will be handled by ConnectionForm's submit button
                destroyOnClose // Reset form state when modal is closed
            >
                <ConnectionForm
                    key={editingConnection?.id || 'new'} // Force re-render when editingConnection changes
                    onSave={handleSave} // Pass save handler
                    onCancel={handleCancel} // Pass cancel handler to form
                    initialData={editingConnection || undefined} // Pass initial data for editing
                />
            </Modal>
        </div>
    );
};

export default ConnectionManagementPage; 