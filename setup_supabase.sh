#!/bin/bash
# Quick setup script for Supabase connection

set -e

echo "=========================================="
echo "Supabase Connection Setup"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "Error: Please run this script from the dv/ directory"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env from template..."
    cp backend/env.supabase.template backend/.env
    echo "✓ Created backend/.env"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit backend/.env with your credentials!"
    echo ""
    echo "Get these from your Supabase dashboard:"
    echo "1. Service Role Key: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/api"
    echo "2. JWT Secret: Same page as above"
    echo "3. Database Password: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/database"
    echo ""
    echo "Then update these lines in backend/.env:"
    echo "  - SUPABASE_SERVICE_ROLE_KEY"
    echo "  - SUPABASE_JWT_SECRET"
    echo "  - DATABASE_URL (replace YOUR_PASSWORD_HERE)"
    echo "  - ENCRYPTION_KEY (generate with command shown in file)"
    echo "  - OPENAI_API_KEY (or another transcription provider)"
    echo ""
    read -p "Press Enter when you've updated backend/.env..."
else
    echo "✓ backend/.env already exists"
fi

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✓ Created venv"
fi

# Activate venv and install dependencies
echo ""
echo "Installing Python dependencies..."
cd backend
source venv/bin/activate

if [ ! -f "venv/.installed" ]; then
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch venv/.installed
    echo "✓ Installed dependencies"
else
    echo "✓ Dependencies already installed"
fi

# Test connection
echo ""
echo "=========================================="
echo "Testing Supabase Connection"
echo "=========================================="
echo ""

python scripts/test_connection.py

# Ask if they want to run migrations
echo ""
read -p "Do you want to run database migrations now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running migrations..."
    python scripts/migrate.py
    echo ""
    echo "✓ Migrations completed"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Redis (in a new terminal):"
echo "   redis-server"
echo ""
echo "2. Start the API (in a new terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Start Celery worker (in a new terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   celery -A app.worker.celery_app worker --loglevel=info"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "5. View API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "See SUPABASE_SETUP.md for detailed usage instructions."
echo ""





