import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ticketsAPI, mlAPI } from '../services/api';

function CreateTicket() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    subject: '',
    description: '',
  });
  const [prediction, setPrediction] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const analyzeTicket = async () => {
    if (!formData.description) return;
    
    setAnalyzing(true);
    try {
      const [classResponse, sentimentResponse] = await Promise.all([
        mlAPI.classify(formData.description),
        mlAPI.analyzeSentiment(formData.description)
      ]);
      
      setPrediction({
        category: classResponse.data.category,
        confidence: classResponse.data.confidence,
        sentiment: sentimentResponse.data.sentiment,
        urgency: sentimentResponse.data.urgency_score
      });
    } catch (error) {
      console.error('Error analyzing ticket:', error);
    }
    setAnalyzing(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      await ticketsAPI.create(formData);
      alert('Ticket created successfully!');
      navigate('/tickets');
    } catch (error) {
      console.error('Error creating ticket:', error);
      alert('Failed to create ticket. Please try again.');
    }
    setSubmitting(false);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Create New Ticket</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Customer Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Customer Name *
              </label>
              <input
                type="text"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address *
              </label>
              <input
                type="email"
                name="customer_email"
                value={formData.customer_email}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Ticket Details</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject *
              </label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <button
              type="button"
              onClick={analyzeTicket}
              disabled={analyzing || !formData.description}
              className="btn-secondary"
            >
              {analyzing ? '🔄 Analyzing...' : '🤖 AI Analysis'}
            </button>

            {prediction && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">AI Predictions</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-blue-600">Category:</span>
                    <span className="ml-2 font-medium">{prediction.category}</span>
                    <span className="ml-1 text-gray-500">({(prediction.confidence * 100).toFixed(0)}%)</span>
                  </div>
                  <div>
                    <span className="text-blue-600">Sentiment:</span>
                    <span className="ml-2 font-medium">{prediction.sentiment}</span>
                  </div>
                  <div>
                    <span className="text-blue-600">Urgency:</span>
                    <span className="ml-2 font-medium">{(prediction.urgency * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex space-x-4">
          <button type="submit" disabled={submitting} className="btn-primary flex-1">
            {submitting ? 'Creating...' : '✅ Create Ticket'}
          </button>
          <button type="button" onClick={() => navigate('/tickets')} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateTicket;
