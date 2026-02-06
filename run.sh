#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# Start the main application with waitress
echo "Starting Waitress server on port 5002..."
if [ -d "venv" ]; then
    ./venv/bin/waitress-serve --host 0.0.0.0 --port 5002 app:app
else
    waitress-serve --host 0.0.0.0 --port 5002 app:app
fi

