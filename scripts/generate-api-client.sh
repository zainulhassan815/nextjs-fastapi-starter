#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "Fetching OpenAPI spec from $BACKEND_URL..."
curl -s "$BACKEND_URL/openapi.json" -o "$FRONTEND_DIR/openapi.json"

echo "Preprocessing OpenAPI spec (clean operation IDs)..."
node "$SCRIPT_DIR/preprocess-openapi.js" "$FRONTEND_DIR/openapi.json"

echo "Generating TypeScript SDK..."
cd "$FRONTEND_DIR" && npx openapi-ts

echo "SDK generated at frontend/lib/api/generated/"
