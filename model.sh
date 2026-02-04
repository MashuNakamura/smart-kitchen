#!/bin/bash

# Force the script to run from the current folder
cd "$(dirname "$0")"

# Load environment variables from .env file
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# Run the model server
echo "Starting Model Server..."
# Assuming python3 is the venv python or system python capable of running the model
# Ideally, we should use the venv python if it exists
if [ -d "venv" ]; then
    ./venv/bin/python model_server.py
else
    python3 model_server.py
fi
