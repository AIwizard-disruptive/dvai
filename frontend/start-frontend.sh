#!/bin/bash

# Start Frontend on Port 8000
# Disruptive Ventures Command Center

echo "🚀 Starting Disruptive Ventures Command Center (Frontend)"
echo "=================================================="
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Set port to 8000
export PORT=8000

echo "🌐 Starting Next.js development server on port 8000..."
echo "📍 URL: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Next.js on port 8000
npm run dev -- -p 8000


