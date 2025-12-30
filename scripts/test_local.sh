#!/bin/bash
# Test script for The Sovereign Council
# Run this after starting Ollama with at least one model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "=== The Sovereign Council - Local Test ==="
echo ""

# Check if Ollama is running
echo "Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  Ollama is running"
    MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; print(', '.join([m['name'] for m in json.load(sys.stdin).get('models', [])]))" 2>/dev/null || echo "unable to parse")
    echo "  Available models: $MODELS"
else
    echo "  ERROR: Ollama is not running at localhost:11434"
    echo "  Start Ollama with: ollama serve"
    exit 1
fi

echo ""

# Change to backend directory
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]" -q

# Run unit tests
echo ""
echo "=== Running Unit Tests ==="
pytest tests/ -v --ignore=tests/test_integration.py

# Run integration tests
echo ""
echo "=== Running Integration Tests ==="
pytest tests/test_integration.py -v -s

echo ""
echo "=== All tests passed! ==="
