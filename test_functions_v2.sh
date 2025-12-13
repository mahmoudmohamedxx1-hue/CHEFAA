#!/bin/bash

SUPABASE_URL="https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

# First get a valid user token by logging in
echo "Logging in to get auth token..."
AUTH_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "apikey: ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cmrgiuds@minimax.com",
    "password": "fWOWk3jQFG"
  }')

ACCESS_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get access token"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

echo "Got access token successfully"
echo ""

# Test all 6 functions with authentication
echo "1. Testing enhanced-ehr-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/enhanced-ehr-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_ehr_connections"}' | jq '.'
echo ""

echo "2. Testing medical-device-connectivity..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/medical-device-connectivity" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_latest_readings","data":{}}' | jq '.'
echo ""

echo "3. Testing real-time-monitoring..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/real-time-monitoring" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_monitoring_dashboard","data":{}}' | jq '.'
echo ""

echo "4. Testing telemedicine-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/telemedicine-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_sessions","data":{}}' | jq '.'
echo ""

echo "5. Testing lab-results-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/lab-results-integration" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_lab_results","data":{}}' | jq '.'
echo ""

echo "6. Testing iot-device-connectivity..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/iot-device-connectivity" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_devices","data":{}}' | jq '.'
echo ""

echo "All tests complete!"
