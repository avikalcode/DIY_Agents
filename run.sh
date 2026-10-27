#!/bin/bash

# Default to 'dev' if no argument is passed
ENV=${1:-dev}

echo "🚀 Starting Agentic-Ladder in [$ENV] environment..."
APP_ENV=$ENV docker compose up --build