#!/bin/bash

# AutoSupport Quick Start Script
# This script sets up and runs the entire application

set -e

echo "🚀 AutoSupport Quick Start"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
fi

# Start with Docker Compose
echo -e "${BLUE}🐳 Starting services with Docker Compose...${NC}"
docker-compose up -d

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📊 Access the application:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Grafana:  http://localhost:3001 (admin/admin)"
echo "   - MLflow:   http://localhost:5000"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart: docker-compose restart"
echo ""
echo "📝 Next steps:"
echo "   1. Wait for all services to be healthy (30-60 seconds)"
echo "   2. Train ML models: docker-compose exec backend python ml/train_models.py"
echo "   3. Seed database: docker-compose exec backend python scripts/seed_data.py"
echo "   4. Open http://localhost:3000 in your browser"
echo ""
