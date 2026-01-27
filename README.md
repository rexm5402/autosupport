# AutoSupport: AI-Powered Customer Support Ticket Routing & Insight System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org/)

## 🚀 Overview

AutoSupport is an intelligent customer support system that automatically classifies, prioritizes, and routes support tickets using machine learning. It features smart response suggestions, real-time analytics, and agent performance tracking.

### ✨ Key Features

- **Automatic Ticket Classification**: Multi-class ML model classifies tickets into categories (Billing, Technical, Account, etc.)
- **Sentiment Analysis**: Detects customer emotion and urgency
- **Smart Routing**: AI-powered agent assignment based on expertise and workload
- **Response Suggestions**: RAG-based system suggests responses from knowledge base
- **Real-time Analytics**: Dashboard with insights, trends, and performance metrics
- **Microservices Architecture**: Scalable, containerized services
- **MLOps Pipeline**: Model versioning, monitoring, and retraining capabilities

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  API Gateway │────▶│   Backend   │
│   (React)   │     │   (FastAPI)  │     │  Services   │
└─────────────┘     └──────────────┘     └─────────────┘
                             │                    │
                             ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   ML Service │     │  PostgreSQL │
                    │  (Inference)  │     │  Database   │
                    └──────────────┘     └─────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   ChromaDB   │
                    │ (Vector Store)│
                    └──────────────┘
```

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery + RabbitMQ
- **ORM**: SQLAlchemy

### Machine Learning
- **Classification**: DistilBERT (HuggingFace)
- **Sentiment Analysis**: Pre-trained transformer models
- **Vector Store**: ChromaDB
- **Embeddings**: Sentence-Transformers
- **Experiment Tracking**: MLflow

### Frontend
- **Framework**: React 18
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **State Management**: React Context API
- **HTTP Client**: Axios

### DevOps
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Deployment**: Railway/Render

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 14+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/autosupport.git
cd autosupport
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose (Recommended)**
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Train ML models (first time only)
python ml/train_models.py

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📊 Dataset

The project uses customer support ticket datasets. You can use:

1. **Kaggle**: Customer Support on Twitter dataset
2. **Bitext**: Customer Support Dataset
3. **Custom**: Add your own tickets to `data/tickets.csv`

Place your dataset in `data/tickets.csv` with columns:
- `text`: Ticket content
- `category`: Category label
- `priority`: Priority level (optional)

## 🧪 Training Models

```bash
cd backend

# Train classification model
python ml/train_models.py

# View experiment results in MLflow
mlflow ui
# Navigate to http://localhost:5000
```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/v1/tickets              - Create new ticket
GET    /api/v1/tickets              - List all tickets
GET    /api/v1/tickets/{id}         - Get ticket details
PUT    /api/v1/tickets/{id}/assign  - Assign ticket to agent
POST   /api/v1/classify             - Classify ticket text
GET    /api/v1/analytics            - Get analytics data
POST   /api/v1/suggest-response     - Get AI response suggestion
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/autosupport

# Redis
REDIS_URL=redis://localhost:6379/0

# ML Models
MODEL_PATH=./models
CLASSIFICATION_MODEL=distilbert-base-uncased
EMBEDDING_MODEL=all-MiniLM-L6-v2

# API
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-here
```

## 📈 Monitoring

The project includes built-in monitoring:

- **Prometheus**: Metrics collection (http://localhost:9090)
- **Grafana**: Dashboards (http://localhost:3001)
  - Default credentials: admin/admin
- **MLflow**: ML experiment tracking (http://localhost:5000)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Using Docker

```bash
# Build and push images
docker build -t autosupport-backend:latest ./backend
docker build -t autosupport-frontend:latest ./frontend

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

The project is configured for easy deployment to:
- **Railway**: One-click deployment
- **Render**: Backend + Database
- **Vercel**: Frontend hosting

See `docs/deployment.md` for detailed instructions.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Project Structure

```
autosupport/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api/                 # API routes
│   │   ├── core/                # Core configs
│   │   └── services/            # Business logic
│   ├── ml/
│   │   ├── train_models.py      # Model training
│   │   ├── inference.py         # Prediction service
│   │   └── rag_system.py        # RAG implementation
│   └── models/                  # Database models
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   └── services/            # API services
│   └── public/
├── data/                        # Training data
├── docker/                      # Docker configs
├── monitoring/                  # Grafana dashboards
└── scripts/                     # Utility scripts
```



## 🙏 Acknowledgments

- HuggingFace for transformer models
- FastAPI for the amazing web framework
- The open-source community

## 📧 Contact

Your Name - Aryan Murugesh

Project Link: [https://github.com/yourusername/autosupport](https://github.com/rexm5402/autosupport)

---

⭐ If you find this project helpful, please consider giving it a star!
