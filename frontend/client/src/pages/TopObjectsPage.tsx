import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { List, Spin, Alert, Typography, Button, Card } from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import { getDbObjects } from '../services/monitoringApi';
import { DbObjectInfo } from '../types/monitoring';

const { Title, Text } = Typography;

const TopObjectsPage: React.FC = () => {
  const { db_id } = useParams<{ db_id: string }>();
  const [objects, setObjects] = useState<DbObjectInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  // Memoize the calculation of top 10 objects
  const top10Objects = useMemo(() => {
    return objects
      .filter((obj: DbObjectInfo) => obj.size_bytes != null) // Add type annotation
      .sort((a: DbObjectInfo, b: DbObjectInfo) => (b.size_bytes ?? 0) - (a.size_bytes ?? 0)) // Add type annotation
      .slice(0, 10); // Take top 10
  }, [objects]);

  if (!db_id) {
    return <Alert message="Error" description="No database selected. Please select a database first." type="error" showIcon />;
  }

  return (
    <div>
      <Title level={2}>Top 10 Largest Objects (DB ID: {db_id})</Title>

      {error && <Alert message="Error fetching data" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      {loading ? (
        <Spin size="large" />
      ) : top10Objects.length === 0 && !error ? (
        <Alert message="No object size data available to determine top objects." type="info" showIcon />
      ) : (
        <Card
          title="Top 10 Objects by Size"
          extra={
            <Link to={`/objects/${db_id}`}>
              <Button type="primary" icon={<ArrowRightOutlined />}>
                Browse All Objects
              </Button>
            </Link>
          }
        >
          <List
            itemLayout="horizontal"
            dataSource={top10Objects}
            renderItem={(item: DbObjectInfo, index: number) => ( // Add type annotation for item
              <List.Item>
                <List.Item.Meta
                  avatar={<Text strong style={{ minWidth: '25px', textAlign: 'right' }}>{index + 1}.</Text>}
                  title={<Text strong>{item.schema_name}.{item.object_name}</Text>}
                  description={`Type: ${item.object_type}, Owner: ${item.owner}`}
                />
                <div style={{ textAlign: 'right' }}>
                    <Text strong>{item.size_pretty ?? '-'}</Text>
                </div>
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

export default TopObjectsPage; 