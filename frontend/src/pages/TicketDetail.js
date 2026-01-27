import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ticketsAPI } from '../services/api';

function TicketDetail() {
  const { id } = useParams();
  const [ticket, setTicket] = useState(null);
  const [responses, setResponses] = useState([]);
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTicketDetails();
  }, [id]);

  const fetchTicketDetails = async () => {
    try {
      const [ticketRes, responsesRes, suggestionRes] = await Promise.all([
        ticketsAPI.getById(id),
        ticketsAPI.getResponses(id),
        ticketsAPI.suggestResponse(id)
      ]);
      setTicket(ticketRes.data);
      setResponses(responsesRes.data);
      setSuggestion(suggestionRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching ticket:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (!ticket) return <div>Ticket not found</div>;

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">{ticket.subject}</h1>
            <p className="text-gray-500 mt-1">Ticket #{ticket.ticket_number}</p>
          </div>
          <span className={`badge ${ticket.status === 'open' ? 'badge-blue' : ticket.status === 'resolved' ? 'badge-green' : 'badge-yellow'}`}>
            {ticket.status.replace('_', ' ')}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b">
          <div>
            <p className="text-sm text-gray-500">Customer</p>
            <p className="font-medium">{ticket.customer_name}</p>
            <p className="text-sm text-gray-600">{ticket.customer_email}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Category</p>
            <p className="font-medium">{ticket.category ? ticket.category.replace('_', ' ') : 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Priority</p>
            <span className={`badge ${ticket.priority === 'urgent' ? 'badge-red' : ticket.priority === 'high' ? 'badge-yellow' : 'badge-blue'}`}>
              {ticket.priority}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Sentiment</p>
            <p className="font-medium">{ticket.sentiment || 'N/A'}</p>
          </div>
        </div>

        <div>
          <h3 className="font-semibold mb-2">Description</h3>
          <p className="text-gray-700">{ticket.description}</p>
        </div>
      </div>

      {suggestion && (
        <div className="card bg-blue-50 border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">🤖 AI Suggested Response</h3>
          <p className="text-gray-700 mb-2">{suggestion.suggested_text}</p>
          <p className="text-sm text-gray-600">Confidence: {(suggestion.confidence * 100).toFixed(0)}%</p>
        </div>
      )}

      <div className="card">
        <h3 className="font-semibold mb-4">Responses</h3>
        {responses.length === 0 ? (
          <p className="text-gray-500">No responses yet</p>
        ) : (
          <div className="space-y-4">
            {responses.map(response => (
              <div key={response.id} className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="text-sm font-medium text-gray-600">{response.agent_name || 'Customer'}</p>
                <p className="text-gray-800">{response.message}</p>
                <p className="text-xs text-gray-500 mt-1">{new Date(response.created_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default TicketDetail;
