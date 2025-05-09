import React, { useState, useEffect } from 'react';
import {
  DatabaseOutlined,
  PieChartOutlined,
  LockOutlined,
  AreaChartOutlined,
  TableOutlined,
  // TrophyOutlined,
  // TeamOutlined,
  // UserOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Layout, Menu, Breadcrumb, theme, Select, Space, Typography, Alert } from 'antd';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Connection, getConnections } from '../services/connectionApi';

const { Header, Content, Footer, Sider } = Layout;
const { Text } = Typography;

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
  disabled?: boolean
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
    disabled,
  } as MenuItem;
}

const generateMenuItems = (selectedDbId: string | null): MenuItem[] => {
  const items: MenuItem[] = [
    getItem(<Link to="/">Dashboard</Link>, '/', <PieChartOutlined />),
    getItem(
      selectedDbId ? <Link to={`/activity/${selectedDbId}`}>Activity</Link> : 'Activity',
      selectedDbId ? `/activity/${selectedDbId}` : '/activity',
      <AreaChartOutlined />,
      undefined,
      !selectedDbId
    ),
    getItem(
      selectedDbId ? <Link to={`/locks/${selectedDbId}`}>Locks</Link> : 'Locks',
      selectedDbId ? `/locks/${selectedDbId}` : '/locks',
      <LockOutlined />,
      undefined,
      !selectedDbId
    ),
    getItem(
      selectedDbId ? <Link to={`/objects/${selectedDbId}`}>Objects</Link> : 'Objects',
      selectedDbId ? `/objects/${selectedDbId}` : '/objects',
      <TableOutlined />,
      undefined,
      !selectedDbId
    ),
    // getItem(
    //   selectedDbId ? <Link to={`/top-objects/${selectedDbId}`}>Top Objects</Link> : 'Top Objects',
    //   selectedDbId ? `/top-objects/${selectedDbId}` : '/top-objects',
    //   <TrophyOutlined />,
    //   undefined,
    //   !selectedDbId
    // ),
    // Add more monitoring pages here using selectedDbId
  ];

  // Add Connections at the end
  items.push(getItem(<Link to="/connections">Connections</Link>, '/connections', <DatabaseOutlined />));

  return items;
};

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [selectedDbId, setSelectedDbId] = useState<string | null>(null);
  const [loadingConnections, setLoadingConnections] = useState<boolean>(true);
  const [errorConnections, setErrorConnections] = useState<string | null>(null);

  const location = useLocation();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  useEffect(() => {
    const fetchConnections = async () => {
      setLoadingConnections(true);
      setErrorConnections(null);
      try {
        const data = await getConnections();
        setConnections(data || []);
      } catch (err) {
        setErrorConnections(err instanceof Error ? err.message : 'Failed to load connections.');
        console.error("Error fetching connections:", err);
      } finally {
        setLoadingConnections(false);
      }
    };
    fetchConnections();
  }, []);

  useEffect(() => {
    const pathParts = location.pathname.split('/');
    const pageType = pathParts[1];
    const dbIdFromUrl = pathParts[2];
    const knownMonitoringPages = ['locks', 'activity', 'objects', 'top-objects'];

    if (knownMonitoringPages.includes(pageType) && dbIdFromUrl) {
       if (dbIdFromUrl !== selectedDbId) {
          if (connections.length === 0 && !loadingConnections) {
          } else if (connections.some((c: Connection) => String(c.id) === dbIdFromUrl)) {
              setSelectedDbId(dbIdFromUrl);
          } else if (!loadingConnections) {
              console.warn(`DB ID ${dbIdFromUrl} from URL not found in loaded connections.`);
          }
       }
    } else {
        // If path is not a monitoring page or doesn't have db_id, ensure selection is cleared?
        // Or keep the last selection? For now, do nothing.
    }
  }, [location.pathname, connections, loadingConnections, selectedDbId]);

  const handleDbSelectionChange = (value: string) => {
    setSelectedDbId(value);
  };

  const menuItems = generateMenuItems(selectedDbId);

  const pathSnippets = location.pathname.split('/').filter((i: string) => i);
  const breadcrumbItems = [
      <Breadcrumb.Item key="home"><Link to="/">Home</Link></Breadcrumb.Item>,
      ...pathSnippets.map((snippet: string, index: number) => {
        const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
        let breadcrumbName = snippet;
        const pageType = pathSnippets[0];
        const knownMonitoringPages = ['locks', 'activity', 'objects', 'top-objects'];

        if (index === 1 && knownMonitoringPages.includes(pageType)) {
            const dbName = connections.find((c: Connection) => String(c.id) === selectedDbId)?.alias;
            breadcrumbName = selectedDbId ? `DB: ${dbName || selectedDbId}` : snippet;
        } else if (index === 0 && knownMonitoringPages.includes(pageType)) {
             breadcrumbName = pageType.split('-').map((word: string) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        } else {
             breadcrumbName = snippet.charAt(0).toUpperCase() + snippet.slice(1);
        }

        return (
          <Breadcrumb.Item key={url}>
            {index === pathSnippets.length - 1 ? breadcrumbName : <Link to={url}>{breadcrumbName}</Link>}
          </Breadcrumb.Item>
        );
      })
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value: boolean) => setCollapsed(value)}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '6px', textAlign: 'center', lineHeight: '32px', color: 'white', overflow: 'hidden' }}>
          <DatabaseOutlined style={{ marginRight: collapsed ? '0px' : '8px', fontSize: '18px' }} />
          {!collapsed && <span style={{ whiteSpace: 'nowrap' }}>PG Pulse</span>}
        </div>
        <Menu theme="dark" selectedKeys={[location.pathname]} mode="inline" items={menuItems} />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
           <Breadcrumb style={{ margin: '0' }}>
             {breadcrumbItems}
           </Breadcrumb>
           <Space>
             <Text>Monitor DB:</Text>
             <Select
               style={{ width: 200 }}
               placeholder="Select a Database"
               loading={loadingConnections}
               value={selectedDbId}
               onChange={handleDbSelectionChange}
               disabled={loadingConnections || !!errorConnections || connections.length === 0}
             >
               {loadingConnections && <Select.Option key="loading">Loading...</Select.Option>}
               {errorConnections && <Select.Option key="error" disabled>Error</Select.Option>}
               {connections && connections.length === 0 && !loadingConnections && <Select.Option key="none" disabled>No connections</Select.Option>}
               {connections && connections.map((conn: Connection) => (
                 <Select.Option key={conn.id} value={String(conn.id)}>
                   {conn.alias} ({conn.db_name}@{conn.hostname})
                 </Select.Option>
               ))}
             </Select>
             {errorConnections && <Alert message={errorConnections} type="error" showIcon/>}
           </Space>
        </Header>
        <Content style={{ margin: '16px' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          PG Pulse ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 