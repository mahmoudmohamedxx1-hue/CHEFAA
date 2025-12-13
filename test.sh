#!/bin/bash

SUPABASE_URL="https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

echo "=========================================="
echo "SECURITY FUNCTIONS TESTING"
echo "=========================================="
echo ""

# Create/sign in test user
echo "1. Authenticating test user..."
AUTH_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "Content-Type: application/json" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"email":"security-test@chefaa.com","password":"SecureTest123!"}')

TOKEN=$(echo $AUTH_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
USER_ID=$(echo $AUTH_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Creating new user..."
  AUTH_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/signup" \
    -H "Content-Type: application/json" \
    -H "apikey: ${ANON_KEY}" \
    -d '{"email":"security-test@chefaa.com","password":"SecureTest123!"}')
  TOKEN=$(echo $AUTH_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
  USER_ID=$(echo $AUTH_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
fi

echo "User ID: $USER_ID"
echo "Token obtained: ${TOKEN:0:30}..."
echo ""

# Test 1: Rate Limiting
echo "=========================================="
echo "TEST 1: Rate Limiting"
echo "=========================================="
curl -s -X POST "${SUPABASE_URL}/functions/v1/rate-limiting" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"check\",\"endpoint\":\"/api/products\",\"identifier\":\"${USER_ID}\",\"type\":\"user\"}" | jq '.'
echo ""

# Test 2: 2FA Management
echo "=========================================="
echo "TEST 2: 2FA Management - Setup TOTP"
echo "=========================================="
curl -s -X POST "${SUPABASE_URL}/functions/v1/2fa-management" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"action":"setup_totp"}' | jq '.'
echo ""

# Test 3: Threat Detection
echo "=========================================="
echo "TEST 3: Threat Detection"
echo "=========================================="
curl -s -X POST "${SUPABASE_URL}/functions/v1/threat-detection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"analyze\",\"user_id\":\"${USER_ID}\",\"event_type\":\"login\",\"ip_address\":\"192.168.1.100\",\"location\":\"Cairo, Egypt\",\"user_agent\":\"Mozilla/5.0\"}" | jq '.'
echo ""

# Test 4: GDPR Compliance
echo "=========================================="
echo "TEST 4: GDPR Compliance"
echo "=========================================="
curl -s -X POST "${SUPABASE_URL}/functions/v1/gdpr-compliance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"action":"request_data"}' | jq '.'
echo ""

# Test 5: HIPAA Compliance
echo "=========================================="
echo "TEST 5: HIPAA Compliance"
echo "=========================================="
curl -s -X POST "${SUPABASE_URL}/functions/v1/hipaa-compliance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"log_access\",\"patient_id\":\"${USER_ID}\",\"phi_type\":\"prescription\",\"access_type\":\"view\",\"reason\":\"Testing PHI access logging\"}" | jq '.'

echo ""
echo "=========================================="
echo "ALL TESTS COMPLETE"
echo "=========================================="
