#!/bin/sh
set -eu

echo "=================================================="
echo "🛡️  STEP 1: VERIFYING ENVIRONMENT VARIABLES"
echo "=================================================="

# Check if crucial variables are present
if [ -z "${APP_ENV:-}" ]; then
    echo "❌ ERROR: APP_ENV environment variable is missing!" >&2
    exit 1
else
    echo "✅ APP_ENV is verified: ${APP_ENV}"
fi

# (Optional) Print all environment variables for debugging
# Warning: Be careful if you have sensitive production passwords/keys
echo "Full Environment Audit:"
env | sort

echo "=================================================="
echo "📂  STEP 2: RUNNING DIRECTORY INSPECTION (ls)"
echo "=================================================="

# Show the current working directory path
echo "Current Directory Path: $(pwd)"

# Output the file list and permissions
echo "Directory Contents:"
ls -la

echo "=================================================="
echo "🚀  STEP 3: HANDING OVER TO MAIN PROCESS"
echo "=================================================="

# Replaces the shell with your main application command (PID 1)
exec "$@"
