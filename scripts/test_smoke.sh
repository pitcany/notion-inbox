#!/bin/bash
set -e

BASE_URL="${API_URL:-http://127.0.0.1:8787}"

echo "Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'

echo ""
echo "Testing inbox creation..."
curl -s -X POST "$BASE_URL/v1/inbox" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Smoke test entry",
    "content": "This is a test entry created by the smoke test script.",
    "type": "note",
    "project": "Personal",
    "tags": ["test"],
    "source": "manual"
  }' | jq '.'

echo ""
echo "Smoke test complete!"
