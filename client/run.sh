#!/bin/bash
# Startup script for Streamlit API Governance Validator

# Get the script directory (client folder)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the parent directory (project root)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "Starting API Governance Validator UI..."
echo "Project Root: $PROJECT_ROOT"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

# Run streamlit from the client directory but with project root in PYTHONPATH
cd "$SCRIPT_DIR"
uv run streamlit run app.py
