#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

# Start the main application with waitress
waitress-serve --host 0.0.0.0 --port 5000 app:app

# Start the model server
# python3 model_server.py &
