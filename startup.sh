#!/bin/bash
# Telegram Manager Bot - Complete Startup Script
# This script starts Ollama server and the Telegram bot with all features

set -e  # Exit on any error

echo "🚀 Starting Telegram Manager Bot with Ollama..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "telegram_bot_optimized.py" ]; then
    print_error "Please run this script from the tg_manager_v2 directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please create one based on env.template"
    print_status "Copying env.template to .env..."
    cp env.template .env
    print_warning "Please edit .env file with your credentials before continuing"
    exit 1
fi

# Load environment variables
print_status "Loading environment variables..."
source .env

# Check required environment variables
required_vars=("TELEGRAM_BOT_TOKEN" "TELEGRAM_API_ID" "TELEGRAM_API_HASH" "TELEGRAM_PHONE")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables: ${missing_vars[*]}"
    print_status "Please set these in your .env file"
    exit 1
fi

print_success "Environment variables loaded successfully"

# Check if Ollama is installed
print_status "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed. Please install it first:"
    echo "   Visit: https://ollama.ai/download"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

print_success "Ollama is installed"

# Check if Ollama server is running
print_status "Checking Ollama server status..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    print_warning "Ollama server is not running. Starting it..."
    
    # Start Ollama server in background
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for server to start
    print_status "Waiting for Ollama server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama server started successfully"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Failed to start Ollama server after 30 seconds"
            exit 1
        fi
        sleep 1
    done
else
    print_success "Ollama server is already running"
fi

# Check if required model is available
print_status "Checking for required AI model..."
MODEL_NAME=${OLLAMA_MODEL:-"llama3.2:3b"}

if ! ollama list | grep -q "$MODEL_NAME"; then
    print_warning "Model $MODEL_NAME not found. Pulling it..."
    ollama pull "$MODEL_NAME"
    print_success "Model $MODEL_NAME pulled successfully"
else
    print_success "Model $MODEL_NAME is available"
fi

# Test Ollama connection
print_status "Testing Ollama connection..."
if python3 -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print('Ollama connection successful')
        exit(0)
    else:
        print('Ollama connection failed')
        exit(1)
except Exception as e:
    print(f'Ollama connection error: {e}')
    exit(1)
" 2>/dev/null; then
    print_success "Ollama connection test passed"
else
    print_error "Ollama connection test failed"
    exit 1
fi

# Install Python dependencies if needed
print_status "Checking Python dependencies..."
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade dependencies
print_status "Installing/upgrading Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test bot components
print_status "Testing bot components..."
if python3 test_features.py; then
    print_success "All bot components are working correctly"
else
    print_warning "Some tests failed, but continuing with startup..."
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot
print_status "Starting Telegram Manager Bot..."
print_success "Bot is starting with all features enabled:"
echo "   ✅ Chat synchronization"
echo "   ✅ Contact management"
echo "   ✅ Outreach automation"
echo "   ✅ AI analysis with Ollama"
echo "   ✅ Google Sheets integration"
echo "   ✅ Follow-up recommendations"

# Run the bot
python3 start_optimized_bot.py

# Cleanup function
cleanup() {
    print_status "Shutting down..."
    if [ ! -z "$OLLAMA_PID" ]; then
        print_status "Stopping Ollama server..."
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    print_success "Shutdown complete"
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for the bot to finish
wait 