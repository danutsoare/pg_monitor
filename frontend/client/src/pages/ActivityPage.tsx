import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Spin, Alert, Typography, Select, Row, Col } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { getActivity } from '../services/monitoringApi';
import { ActivityPoint } from '../types/monitoring';

const { Title, Text } = Typography;
const { Option } = Select;

const timeRanges = [
  { value: '1h', label: 'Last 1 Hour' },
  { value: '6h', label: 'Last 6 Hours' },
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  // Add more ranges if needed
];

const ActivityPage: React.FC = () => {
  const { db_id } = useParams<{ db_id: string }>();
  const [activityData, setActivityData] = useState<ActivityPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('1h'); // Default time range

  useEffect(() => {
    const fetchActivity = async () => {
      if (!db_id) {
        setError("Database ID not found in URL.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await getActivity(db_id, selectedTimeRange);
        // Format timestamp for display
        const formattedData = data.map(point => ({
          ...point,
          // Format timestamp to a readable format (e.g., HH:mm or MM/DD HH:mm)
          // Adjust formatting based on the selectedTimeRange for clarity
          formattedTimestamp: new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) // Simple example
        }));
        setActivityData(formattedData || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch activity data.');
        console.error("Error fetching activity:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchActivity();
    // TODO: Implement auto-refresh logic (e.g., setInterval)
  }, [db_id, selectedTimeRange]); // Refetch when db_id or time range changes

  const handleTimeRangeChange = (value: string) => {
    setSelectedTimeRange(value);
  };

  if (!db_id) {
     return <Alert message="Error" description="No database selected. Please select a database first." type="error" showIcon />;
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
           <Title level={2}>Database Activity (DB ID: {db_id})</Title>
        </Col>
        <Col>
          <Text>Time Range: </Text>
          <Select value={selectedTimeRange} onChange={handleTimeRangeChange} style={{ width: 150 }}>
            {timeRanges.map(range => (
              <Option key={range.value} value={range.value}>{range.label}</Option>
            ))}
          </Select>
           {/* TODO: Add manual refresh button */}
        </Col>
      </Row>

      {error && <Alert message="Error fetching data" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}

      {loading ? (
        <Spin size="large" />
      ) : activityData.length === 0 && !error ? (
           <Alert message="No activity data available for the selected time range." type="info" showIcon />
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={activityData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="formattedTimestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" name="Total Sessions" stroke="#8884d8" activeDot={{ r: 8 }} />
            {/* Remove lines for keys that don't exist in the response */}
            {/* <Line type="monotone" dataKey="active_sessions" name="Active" stroke="#8884d8" activeDot={{ r: 8 }} /> */}
            {/* <Line type="monotone" dataKey="idle_sessions" name="Idle" stroke="#82ca9d" /> */}
            {/* <Line type="monotone" dataKey="waiting_sessions" name="Waiting" stroke="#ffc658" /> */}
            {/* Add lines for other metrics if available */}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default ActivityPage; 