import { Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd'; // Use AntApp for context
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import ConnectionManagementPage from './pages/ConnectionManagementPage';
import LocksPage from './pages/LocksPage';
import ActivityPage from './pages/ActivityPage';
import ObjectsPage from './pages/ObjectsPage';
import TopObjectsPage from './pages/TopObjectsPage';
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
            <Route path="connections" element={<ConnectionManagementPage />} />
            <Route path="locks/:db_id" element={<LocksPage />} />
            <Route path="activity/:db_id" element={<ActivityPage />} />
            <Route path="objects/:db_id" element={<ObjectsPage />} />
            <Route path="top-objects/:db_id" element={<TopObjectsPage />} />
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