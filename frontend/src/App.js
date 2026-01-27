import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Tickets from './pages/Tickets';
import TicketDetail from './pages/TicketDetail';
import CreateTicket from './pages/CreateTicket';
import Agents from './pages/Agents';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white transition-all duration-300`}>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <h1 className={`text-xl font-bold ${!sidebarOpen && 'hidden'}`}>
                AutoSupport
              </h1>
              <button 
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-400 hover:text-white"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>

          <nav className="mt-8">
            <NavLink to="/" icon="📊" text="Dashboard" sidebarOpen={sidebarOpen} />
            <NavLink to="/tickets" icon="🎫" text="Tickets" sidebarOpen={sidebarOpen} />
            <NavLink to="/create-ticket" icon="➕" text="Create Ticket" sidebarOpen={sidebarOpen} />
            <NavLink to="/agents" icon="👥" text="Agents" sidebarOpen={sidebarOpen} />
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          {/* Header */}
          <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  AI-Powered Customer Support
                </h2>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">Welcome, Admin</span>
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    A
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tickets" element={<Tickets />} />
              <Route path="/tickets/:id" element={<TicketDetail />} />
              <Route path="/create-ticket" element={<CreateTicket />} />
              <Route path="/agents" element={<Agents />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

function NavLink({ to, icon, text, sidebarOpen }) {
  return (
    <Link
      to={to}
      className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
    >
      <span className="text-2xl">{icon}</span>
      {sidebarOpen && <span className="ml-3">{text}</span>}
    </Link>
  );
}

export default App;
