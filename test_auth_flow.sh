#!/bin/bash

SUPABASE_URL="https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

echo "=== Testing Complete Authentication Flow ==="
echo ""

# Step 1: Authenticate
echo "Step 1: Authenticating user..."
AUTH_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "apikey: ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cmrgiuds@minimax.com",
    "password": "fWOWk3jQFG"
  }')

echo "Auth Response:"
echo "$AUTH_RESPONSE" | jq '.' 2>/dev/null || echo "$AUTH_RESPONSE"
echo ""

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  exit 1
fi

echo "✅ Successfully authenticated"
echo "Token preview: ${ACCESS_TOKEN:0:50}..."
echo ""

# Step 2: Test each healthcare integration function
echo "Step 2: Testing Healthcare Integration Functions with Authentication"
echo ""

echo "Test 1: EHR Integration - Get Connections"
curl -s -X POST "${SUPABASE_URL}/functions/v1/enhanced-ehr-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_ehr_connections"}' | jq '.'
echo ""

echo "Test 2: Medical Devices - Get Latest Readings"
curl -s -X POST "${SUPABASE_URL}/functions/v1/medical-device-connectivity" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_latest_readings","data":{}}' | jq '.'
echo ""

echo "Test 3: Real-time Monitoring - Get Dashboard"
curl -s -X POST "${SUPABASE_URL}/functions/v1/real-time-monitoring" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_monitoring_dashboard","data":{}}' | jq '.'
echo ""

echo "Test 4: Telemedicine - Get Sessions"
curl -s -X POST "${SUPABASE_URL}/functions/v1/telemedicine-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_sessions","data":{}}' | jq '.'
echo ""

echo "Test 5: Lab Results - Get Results"
curl -s -X POST "${SUPABASE_URL}/functions/v1/lab-results-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_lab_results","data":{}}' | jq '.'
echo ""

echo "Test 6: IoT Devices - Get Devices"
curl -s -X POST "${SUPABASE_URL}/functions/v1/iot-device-connectivity" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_devices","data":{}}' | jq '.'
echo ""

echo "=== Testing Complete ==="
