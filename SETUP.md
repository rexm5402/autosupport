# AutoSupport Setup Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 10GB free disk space

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd autosupport
```

2. **Run the quick start script**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

3. **Wait for services to start** (30-60 seconds)

4. **Initialize the system**
```bash
# Train ML models
docker-compose exec backend python ml/train_models.py

# Seed database with sample data
docker-compose exec backend python scripts/seed_data.py
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Grafana Dashboards: http://localhost:3001 (admin/admin)
- MLflow: http://localhost:5000

## Manual Setup (if not using Docker)

### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
# Make sure PostgreSQL is running
createdb autosupport

# Update .env with your database credentials
cp ../.env.example .env
# Edit .env file
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Train models**
```bash
python ml/train_models.py
```

6. **Seed database**
```bash
python scripts/seed_data.py
```

7. **Start server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
# Create .env.local
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

3. **Start development server**
```bash
npm start
```

The app will open at http://localhost:3000

## Testing the Application

### 1. Create a Test Ticket
- Go to http://localhost:3000/create-ticket
- Fill in customer details
- Write a ticket description (e.g., "I can't login to my account")
- Click "AI Analysis" to see ML predictions
- Submit the ticket

### 2. View Dashboard
- Go to http://localhost:3000
- See analytics, charts, and trends
- Check ticket distribution

### 3. Manage Agents
- Go to http://localhost:3000/agents
- View agent performance
- See workload distribution

### 4. Explore API
- Visit http://localhost:8000/docs
- Try out the interactive API documentation
- Test classification and sentiment endpoints

## Using Your Own Data

### Training with Custom Dataset

1. **Prepare your CSV file** with columns:
   - `text`: Ticket description
   - `category`: Category label

2. **Train the model**
```bash
docker-compose exec backend python ml/train_models.py /path/to/your/data.csv
```

### Adding Tickets via API

```bash
curl -X POST "http://localhost:8000/api/v1/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "subject": "Cannot access dashboard",
    "description": "I am getting a 403 error when trying to access my dashboard"
  }'
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### ML models not loading
```bash
# Retrain models
docker-compose exec backend python ml/train_models.py

# Check logs
docker-compose logs backend | grep "ML"
```

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in backend/.env
- Verify proxy setting in frontend/package.json

## Production Deployment

### Environment Variables
Set these in production:
```bash
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=<production-db-url>
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

### Using Docker in Production

1. **Build production images**
```bash
docker build -t autosupport-backend:prod ./backend
docker build -t autosupport-frontend:prod ./frontend
```

2. **Deploy to cloud**
- Railway: Connect GitHub repo, auto-deploy
- Render: Import Docker images
- AWS ECS: Use provided task definitions
- Google Cloud Run: Deploy containers

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Monitoring

### Prometheus Metrics
- View at http://localhost:9090
- Query ticket processing times
- Monitor API request rates

### Grafana Dashboards
- Access at http://localhost:3001
- Default credentials: admin/admin
- Import dashboards from `monitoring/grafana/`

### MLflow Tracking
- View at http://localhost:5000
- Track model experiments
- Compare model versions

## Performance Optimization

### Backend
- Enable Redis caching
- Use connection pooling
- Configure worker processes
```bash
uvicorn app.main:app --workers 4
```

### Database
- Create indexes on frequently queried fields
```sql
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_category ON tickets(category);
```

### ML Models
- Use quantized models for faster inference
- Batch prediction requests
- Cache predictions

## Security Best Practices

1. **Change default passwords**
```bash
# Update in .env
SECRET_KEY=<your-secure-key>
DATABASE_PASSWORD=<strong-password>
```

2. **Enable HTTPS** in production

3. **Set up authentication** for API endpoints

4. **Regular backups**
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres autosupport > backup.sql
```

## Getting Help

- Check logs: `docker-compose logs -f`
- Read error messages in browser console
- Review API documentation at `/docs`
- Check GitHub issues
- Contact support@autosupport.com

## Next Steps

1. ✅ Customize the UI with your branding
2. ✅ Train models on your own ticket data
3. ✅ Add email notifications
4. ✅ Integrate with your existing tools
5. ✅ Deploy to production
6. ✅ Set up monitoring and alerts
7. ✅ Create custom analytics dashboards

Happy building! 🚀
