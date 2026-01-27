import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ticketsAPI } from '../services/api';

function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTickets();
  }, [filter]);

  const fetchTickets = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await ticketsAPI.getAll(params);
      setTickets(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tickets:', error);
      setLoading(false);
    }
  };

  const getPriorityBadge = (priority) => {
    const classes = {
      urgent: 'badge badge-red',
      high: 'badge badge-yellow',
      medium: 'badge badge-blue',
      low: 'badge badge-gray',
    };
    return classes[priority] || 'badge badge-gray';
  };

  const getStatusBadge = (status) => {
    const classes = {
      open: 'badge badge-blue',
      in_progress: 'badge badge-yellow',
      resolved: 'badge badge-green',
      closed: 'badge badge-gray',
    };
    return classes[status] || 'badge badge-gray';
  };

  if (loading) {
    return <div className="text-center py-8">Loading tickets...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Support Tickets</h1>
        <Link to="/create-ticket" className="btn-primary">
          ➕ Create Ticket
        </Link>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {['all', 'open', 'in_progress', 'resolved', 'closed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {f.replace('_', ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* Tickets List */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticket #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tickets.map((ticket) => (
                <tr key={ticket.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/tickets/${ticket.id}`} className="text-blue-600 hover:text-blue-800 font-medium">
                      {ticket.ticket_number}
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{ticket.subject}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{ticket.customer_name}</div>
                    <div className="text-sm text-gray-500">{ticket.customer_email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge badge-blue">
                      {ticket.category ? ticket.category.replace('_', ' ') : 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getPriorityBadge(ticket.priority)}>
                      {ticket.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(ticket.status)}>
                      {ticket.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(ticket.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Tickets;
