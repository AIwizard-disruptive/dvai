#!/bin/bash
# Quick finish setup - OpenAI key already configured!

set -e

echo "=========================================="
echo "🚀 Final Setup Steps"
echo "=========================================="
echo ""
echo "✅ OpenAI API key: Already configured!"
echo ""

# Navigate to backend
cd "$(dirname "$0")/backend"

# Copy config file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp env.local.configured .env
    echo "✅ Created .env file"
else
    echo "⚠️  .env already exists - not overwriting"
    echo "   If you want to use the new config, run:"
    echo "   cd backend && cp env.local.configured .env"
fi

echo ""
echo "=========================================="
echo "⚠️  ACTION REQUIRED"
echo "=========================================="
echo ""
echo "You need to add 4 more values to backend/.env:"
echo ""
echo "1️⃣  SUPABASE_SERVICE_ROLE_KEY"
echo "   Get from: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/api"
echo "   Look for 'service_role' key (starts with eyJ...)"
echo ""
echo "2️⃣  SUPABASE_JWT_SECRET"
echo "   Same page, scroll down to 'JWT Secret'"
echo ""
echo "3️⃣  DATABASE_URL password"
echo "   Get from: https://supabase.com/dashboard/project/gqpupmuzriqarmrsuwev/settings/database"
echo "   Replace YOUR_PASSWORD_HERE in the DATABASE_URL line"
echo ""
echo "4️⃣  ENCRYPTION_KEY"
echo "   Generate now? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Generating encryption key..."
    if command -v python3 &> /dev/null; then
        ENCRYPTION_KEY=$(python3 -c "import base64; import os; print(base64.b64encode(os.urandom(32)).decode())")
        echo ""
        echo "✅ Generated encryption key:"
        echo "   $ENCRYPTION_KEY"
        echo ""
        echo "📋 Copy this key and paste it in .env as ENCRYPTION_KEY value"
    else
        echo "❌ Python3 not found. Generate manually with:"
        echo "   python3 -c \"import base64; import os; print(base64.b64encode(os.urandom(32)).decode())\""
    fi
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Edit backend/.env and add the 4 values above"
echo ""
echo "2. Run the setup:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Test connection:"
echo "   python scripts/test_connection.py"
echo ""
echo "4. Run migrations:"
echo "   python scripts/migrate.py"
echo ""
echo "5. Start services (in separate terminals):"
echo "   Terminal 1: uvicorn app.main:app --reload"
echo "   Terminal 2: redis-server"
echo "   Terminal 3: celery -A app.worker.celery_app worker --loglevel=info"
echo ""
echo "6. Test API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "See SETUP_NOW.md for detailed instructions!"
echo ""




