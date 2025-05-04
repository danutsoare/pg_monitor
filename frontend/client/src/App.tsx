import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd'; // Use AntApp for context
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import ConnectionsPage from './pages/ConnectionsPage';
import './App.css';

function App() {
  return (
    <ConfigProvider
      theme={{
        // Customize Ant Design theme here if needed
        token: {
          // Seed Token
          // colorPrimary: '#00b96b',
          // borderRadius: 2,
        },
      }}
    >
      <AntApp> { /* AntApp provides context for message, notification etc. */ }
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="connections" element={<ConnectionsPage />} />
            {/* Add other routes here */}
            {/* Example: <Route path="objects" element={<ObjectsPage />} /> */}
            {/* Add a catch-all/404 route if needed */}
            {/* <Route path="*" element={<NotFoundPage />} /> */}
          </Route>
        </Routes>
      </AntApp>
    </ConfigProvider>
  );
}

export default App; 