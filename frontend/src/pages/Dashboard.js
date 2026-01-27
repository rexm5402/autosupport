import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsAPI } from '../services/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await analyticsAPI.getDashboard();
      setAnalytics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return <div className="text-center text-gray-600">No data available</div>;
  }

  const { ticket_stats, agent_stats, trends } = analytics;

  // Prepare chart data
  const categoryData = Object.entries(ticket_stats.tickets_by_category || {}).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value
  }));

  const priorityData = Object.entries(ticket_stats.tickets_by_priority || {}).map(([name, value]) => ({
    name,
    value
  }));

  const sentimentData = Object.entries(ticket_stats.sentiment_distribution || {}).map(([name, value]) => ({
    name,
    value
  }));

  const trendData = Object.entries(trends.daily_ticket_count || {}).slice(-7).map(([date, count]) => ({
    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    tickets: count
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your support system</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Tickets"
          value={ticket_stats.total_tickets}
          icon="🎫"
          color="blue"
        />
        <StatCard
          title="Open Tickets"
          value={ticket_stats.open_tickets}
          icon="📭"
          color="yellow"
        />
        <StatCard
          title="Resolved"
          value={ticket_stats.resolved_tickets}
          icon="✅"
          color="green"
        />
        <StatCard
          title="Avg Resolution Time"
          value={`${ticket_stats.average_resolution_time}h`}
          icon="⏱️"
          color="purple"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ticket Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Ticket Trends (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="tickets" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Tickets by Category</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Tickets by Priority</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={priorityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Analysis */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Customer Sentiment</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.name === 'positive' ? '#10b981' : entry.name === 'negative' ? '#ef4444' : '#f59e0b'} 
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Performance */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Top Performing Agents</h3>
          <Link to="/agents" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            View All →
          </Link>
        </div>
        <div className="space-y-3">
          {agent_stats.top_performers && agent_stats.top_performers.slice(0, 3).map((agent, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                  {agent.name.charAt(0)}
                </div>
                <div>
                  <p className="font-medium">{agent.name}</p>
                  <p className="text-sm text-gray-500">{agent.tickets_handled} tickets handled</p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center space-x-1">
                  <span className="text-yellow-500">⭐</span>
                  <span className="font-medium">{agent.satisfaction_score.toFixed(1)}</span>
                </div>
                <p className="text-sm text-gray-500">{agent.avg_resolution_time.toFixed(1)}h avg</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/create-ticket" className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 transition-all">
            <div className="text-3xl mb-2">➕</div>
            <div className="font-medium">Create New Ticket</div>
          </Link>
          <Link to="/tickets?status=open" className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 transition-all">
            <div className="text-3xl mb-2">📭</div>
            <div className="font-medium">View Open Tickets</div>
          </Link>
          <Link to="/agents" className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 transition-all">
            <div className="text-3xl mb-2">👥</div>
            <div className="font-medium">Manage Agents</div>
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`text-4xl ${colorClasses[color]} rounded-full w-16 h-16 flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
