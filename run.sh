#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# Start the main application with waitress
echo "Starting Waitress server on port 5000..."
if [ -d "venv" ]; then
    ./venv/bin/waitress-serve --host 0.0.0.0 --port 5000 app:app
else
    waitress-serve --host 0.0.0.0 --port 5000 app:app
fi

