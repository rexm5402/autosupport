# AutoSupport: AI-Powered Customer Support Ticket Routing & Insight System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org/)

## Live Demo

**[https://autosupport-42f43k935-aryan-murugeshs-projects.vercel.app](https://autosupport-42f43k935-aryan-murugeshs-projects.vercel.app)**

## Overview

AutoSupport is an intelligent customer support system that automatically classifies, prioritizes, and routes support tickets. It features AI-powered response suggestions via Groq, real-time analytics, and agent performance tracking.

### Key Features

- **Automatic Ticket Classification**: Classifies tickets into categories (Billing, Technical, Account, Complaint, Feature Request)
- **Sentiment Analysis**: Detects customer emotion and urgency score
- **Smart Routing**: Agent assignment based on expertise and workload
- **AI Response Suggestions**: Groq-powered response generation with template fallback
- **Real-time Analytics**: Dashboard with insights, trends, and performance metrics

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  PostgreSQL │
│  (React)    │     │  (FastAPI)   │     │ (Supabase)  │
│  (Vercel)   │     │  (Render)    │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Groq AI    │
                    │ (LLM API)    │
                    └──────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **AI**: Groq API (llama3-8b-8192)
- **Hosting**: Render (free tier, always-on via UptimeRobot)

### Frontend
- **Framework**: React 18
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Hosting**: Vercel

## API Endpoints

```
POST   /api/v1/tickets                    - Create new ticket
GET    /api/v1/tickets                    - List all tickets
GET    /api/v1/tickets/{id}               - Get ticket details
PUT    /api/v1/tickets/{id}               - Update ticket
POST   /api/v1/tickets/{id}/assign        - Assign ticket to agent
POST   /api/v1/tickets/{id}/suggest-response - Get AI response suggestion
GET    /api/v1/agents                     - List agents
GET    /api/v1/analytics/dashboard        - Get analytics data
POST   /api/v1/ml/classify                - Classify ticket text
POST   /api/v1/ml/sentiment               - Analyze sentiment
GET    /health                            - Health check
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env
# Edit .env with your DATABASE_URL, GROQ_API_KEY, SECRET_KEY

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variable
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm start
```

## Environment Variables

### Backend (Render)
```env
DATABASE_URL=postgresql://...   # Supabase connection string
GROQ_API_KEY=gsk_...            # Groq API key (console.groq.com)
SECRET_KEY=your-secret-key
```

### Frontend (Vercel)
```env
REACT_APP_API_URL=https://autosupport.onrender.com/api/v1
```

## Deployment

This project is deployed for free using:

| Service | Platform | Purpose |
|---------|----------|---------|
| Frontend | Vercel | React app hosting |
| Backend | Render (free tier) | FastAPI server |
| Database | Supabase (free tier) | PostgreSQL |
| Uptime | UptimeRobot | Keeps Render awake |

## Project Structure

```
autosupport/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── api/v1/          # API routes
│   │   ├── core/            # Config & database
│   │   └── services/        # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Page components
│   │   └── services/        # API client
│   └── vercel.json
├── render.yaml               # Render deployment config
└── README.md
```

## Contact

Aryan Murugesh — [github.com/rexm5402/autosupport](https://github.com/rexm5402/autosupport)

---

⭐ If you find this project helpful, please consider giving it a star!
