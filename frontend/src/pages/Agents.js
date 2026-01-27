import React, { useState, useEffect } from 'react';
import { agentsAPI } from '../services/api';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await agentsAPI.getAll();
      setAgents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching agents:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading agents...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Support Agents</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map(agent => (
          <div key={agent.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {agent.name.charAt(0)}
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{agent.name}</h3>
                  <p className="text-sm text-gray-500">{agent.email}</p>
                </div>
              </div>
              <span className={`badge ${agent.is_available ? 'badge-green' : 'badge-gray'}`}>
                {agent.is_available ? 'Available' : 'Busy'}
              </span>
            </div>

            <div className="space-y-2 mb-4">
              <div>
                <p className="text-sm text-gray-500">Expertise</p>
                <p className="text-sm font-medium">{agent.expertise}</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-gray-500">Tickets Handled</p>
                  <p className="font-semibold">{agent.total_tickets_handled}</p>
                </div>
                <div>
                  <p className="text-gray-500">Satisfaction</p>
                  <div className="flex items-center">
                    <span className="text-yellow-500 mr-1">⭐</span>
                    <span className="font-semibold">{agent.customer_satisfaction_score.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Avg Resolution Time</span>
                <span className="font-medium">{agent.average_resolution_time.toFixed(1)}h</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Agents;
