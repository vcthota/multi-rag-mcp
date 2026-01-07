#!/bin/bash
# Quick deployment script for API Governance service

set -e

echo "🐳 API Governance Docker Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.docker .env
    echo -e "${RED}❗ IMPORTANT: Please edit .env file and add your OPENAI_API_KEY${NC}"
    echo ""
    read -p "Press Enter to edit .env file now, or Ctrl+C to exit and edit manually..."
    ${EDITOR:-nano} .env
fi

# Verify OpenAI API key is set
if ! grep -q "OPENAI_API_KEY.*sk-" .env; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY not set in .env file${NC}"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration found${NC}"
echo ""

# Ask user what to do
echo "What would you like to do?"
echo "1) Build and start services (first time setup)"
echo "2) Start existing services"
echo "3) Stop services"
echo "4) View logs"
echo "5) Clean up (remove all containers and volumes)"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔨 Building Docker images..."
        docker-compose -f docker-compose.api-governance.yml build
        
        echo ""
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.api-governance.yml up -d
        
        echo ""
        echo "⏳ Waiting for services to be healthy..."
        sleep 10
        
        echo ""
        echo "🔍 Checking service status..."
        docker-compose -f docker-compose.api-governance.yml ps
        
        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "📊 Services available at:"
        echo "  • API Backend: http://localhost:8000"
        echo "  • API Docs: http://localhost:8000/docs"
        echo "  • Streamlit UI: http://localhost:8501"
        echo ""
        echo "📝 To view logs: ./deploy.sh (select option 4)"
        ;;
        
    2)
        echo ""
        echo "🚀 Starting services..."
        docker-compose -f docker-compose.api-governance.yml up -d
        
        echo ""
        echo "🔍 Checking service status..."
        docker-compose -f docker-compose.api-governance.yml ps
        
        echo ""
        echo -e "${GREEN}✅ Services started!${NC}"
        ;;
        
    3)
        echo ""
        echo "🛑 Stopping services..."
        docker-compose -f docker-compose.api-governance.yml down
        
        echo ""
        echo -e "${GREEN}✅ Services stopped!${NC}"
        ;;
        
    4)
        echo ""
        echo "📝 Showing logs (Ctrl+C to exit)..."
        docker-compose -f docker-compose.api-governance.yml logs -f
        ;;
        
    5)
        echo ""
        echo -e "${YELLOW}⚠️  This will remove all containers, networks, and volumes!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        
        if [ "$confirm" = "yes" ]; then
            echo ""
            echo "🗑️  Cleaning up..."
            docker-compose -f docker-compose.api-governance.yml down -v
            docker image prune -f
            
            echo ""
            echo -e "${GREEN}✅ Cleanup complete!${NC}"
        else
            echo "Cancelled."
        fi
        ;;
        
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

exit 0
