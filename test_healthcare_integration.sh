#!/bin/bash

echo "Testing Healthcare Integration Edge Functions..."
echo ""

# Get Supabase credentials from environment
SUPABASE_URL="https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

# Function 1: Enhanced EHR Integration
echo "1. Testing enhanced-ehr-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/enhanced-ehr-integration" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_ehr_connections"}' | jq '.'
echo ""

# Function 2: Medical Device Connectivity
echo "2. Testing medical-device-connectivity..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/medical-device-connectivity" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_latest_readings","data":{}}' | jq '.'
echo ""

# Function 3: Real-time Monitoring
echo "3. Testing real-time-monitoring..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/real-time-monitoring" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_monitoring_dashboard","data":{}}' | jq '.'
echo ""

# Function 4: Telemedicine Integration
echo "4. Testing telemedicine-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/telemedicine-integration" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_sessions","data":{}}' | jq '.'
echo ""

# Function 5: Lab Results Integration
echo "5. Testing lab-results-integration..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/lab-results-integration" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_lab_results","data":{}}' | jq '.'
echo ""

# Function 6: IoT Device Connectivity
echo "6. Testing iot-device-connectivity..."
curl -s -X POST "${SUPABASE_URL}/functions/v1/iot-device-connectivity" \
  -H "Authorization: Bearer ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action":"get_devices","data":{}}' | jq '.'
echo ""

echo "Testing complete!"
