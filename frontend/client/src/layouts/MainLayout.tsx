import React, { useState } from 'react';
import {
  DesktopOutlined,
  DatabaseOutlined,
  PieChartOutlined,
  // TeamOutlined,
  // UserOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Layout, Menu, Breadcrumb, theme } from 'antd';
import { Outlet, Link, useLocation } from 'react-router-dom';

const { Header, Content, Footer, Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
  } as MenuItem;
}

const items: MenuItem[] = [
  getItem(<Link to="/">Dashboard</Link>, '/', <PieChartOutlined />),
  getItem(<Link to="/connections">Connections</Link>, '/connections', <DatabaseOutlined />),
  // Add more items here as needed
  // getItem('Option 2', '2', <DesktopOutlined />),
  // getItem('User', 'sub1', <UserOutlined />, [
  //   getItem('Tom', '3'),
  //   getItem('Bill', '4'),
  //   getItem('Alex', '5'),
  // ]),
  // getItem('Team', 'sub2', <TeamOutlined />, [getItem('Team 1', '6'), getItem('Team 2', '8')]),
  // getItem('Files', '9', <FileOutlined />),
];

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation(); // Get current location
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  // Determine the breadcrumb path
  const pathSnippets = location.pathname.split('/').filter((i: string) => i);
  const breadcrumbItems = [
    <Breadcrumb.Item key="home">
      <Link to="/">Home</Link>
    </Breadcrumb.Item>,
    ...pathSnippets.map((snippet: string, index: number) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      // Find matching menu item label for breadcrumb name
      // Simple match for now, might need refinement for complex routes
      let breadcrumbName = snippet.charAt(0).toUpperCase() + snippet.slice(1);
      const findItemLabel = (itemsToCheck: MenuItem[], key: string): string | null => {
        for (const item of itemsToCheck) {
          if (item?.key === key) {
            // Assuming label is a Link component
            return (item.label as React.ReactElement)?.props?.children as string || breadcrumbName;
          }
          if (item?.children) {
            const found = findItemLabel(item.children, key);
            if (found) return found;
          }
        }
        return null;
      };
      const matchedLabel = findItemLabel(items, url);
      breadcrumbName = matchedLabel || breadcrumbName;

      return (
        <Breadcrumb.Item key={url}>
          {index === pathSnippets.length - 1 ? (
            breadcrumbName
          ) : (
            <Link to={url}>{breadcrumbName}</Link>
          )}
        </Breadcrumb.Item>
      );
    }),
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value: boolean) => setCollapsed(value)}>
        <div style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '6px', textAlign: 'center', lineHeight: '32px', color: 'white', overflow: 'hidden' }}>
          PG Mon
        </div>
        <Menu theme="dark" defaultSelectedKeys={[location.pathname]} mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer }}>
          <Breadcrumb style={{ margin: '16px 0' }}>
             {breadcrumbItems}
          </Breadcrumb>
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
            <Outlet /> { /* Child routes will render here */ }
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          PostgreSQL Monitor ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 