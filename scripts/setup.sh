#!/bin/bash
# FRACTO Voice Agent Automation Setup Script

echo "🚀 Setting up FRACTO Voice Agent Automation System..."

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file from example
echo "⚙️  Creating environment configuration..."
cp .env.example .env
echo "Please edit backend/.env with your API keys and configuration"

# Setup frontend
echo "📦 Setting up frontend dependencies..."
cd ../frontend
npm install

# Create database
echo "🗄️  Setting up database..."
cd ../backend
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run 'docker-compose up' to start all services"
echo "3. Access the application at http://localhost:3000"
