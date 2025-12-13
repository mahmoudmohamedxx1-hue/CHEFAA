#!/bin/bash

SUPABASE_URL="https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

echo "======================================================================"
echo "SECURITY EDGE FUNCTIONS - COMPREHENSIVE TEST SUITE"
echo "======================================================================"
echo ""

# Step 1: Authenticate
echo "[Step 1/6] Authenticating test user..."
AUTH_RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "Content-Type: application/json" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"email":"cmrgiuds@minimax.com","password":"fWOWk3jQFG"}')

TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
USER_ID=$(echo "$AUTH_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "[FAILED] Could not authenticate"
  exit 1
fi

echo "[SUCCESS] Authenticated successfully"
echo "  User ID: $USER_ID"
echo "  Email: cmrgiuds@minimax.com"
echo ""

# Test 1: Rate Limiting
echo "======================================================================"
echo "[Step 2/6] TEST 1: Rate Limiting - Check Request Limits"
echo "======================================================================"
RESULT=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/rate-limiting" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"check\",\"endpoint\":\"/api/products\",\"identifier\":\"${USER_ID}\",\"type\":\"user\"}")
  
HTTP_CODE=$(echo "$RESULT" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE=$(echo "$RESULT" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE"
if [ "$HTTP_CODE" = "200" ]; then 
  echo "Result: [PASS]"
  TEST1="PASS"
else 
  echo "Result: [FAIL]"
  TEST1="FAIL"
fi
echo ""

# Test 2: 2FA Management
echo "======================================================================"
echo "[Step 3/6] TEST 2: 2FA Management - Setup TOTP"
echo "======================================================================"
RESULT=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/2fa-management" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"action":"setup_totp"}')
  
HTTP_CODE=$(echo "$RESULT" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE=$(echo "$RESULT" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE"
if [ "$HTTP_CODE" = "200" ]; then 
  echo "Result: [PASS]"
  TEST2="PASS"
else 
  echo "Result: [FAIL]"
  TEST2="FAIL"
fi
echo ""

# Test 3: Threat Detection
echo "======================================================================"
echo "[Step 4/6] TEST 3: Threat Detection - Analyze Login Behavior"
echo "======================================================================"
RESULT=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/threat-detection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"analyze\",\"user_id\":\"${USER_ID}\",\"event_type\":\"login\",\"ip_address\":\"192.168.1.100\",\"location\":\"Cairo, Egypt\",\"user_agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\"}")
  
HTTP_CODE=$(echo "$RESULT" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE=$(echo "$RESULT" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE"
if [ "$HTTP_CODE" = "200" ]; then 
  echo "Result: [PASS]"
  TEST3="PASS"
else 
  echo "Result: [FAIL]"
  TEST3="FAIL"
fi
echo ""

# Test 4: GDPR Compliance
echo "======================================================================"
echo "[Step 5/6] TEST 4: GDPR Compliance - Data Access Request"
echo "======================================================================"
RESULT=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/gdpr-compliance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d '{"action":"request_data"}')
  
HTTP_CODE=$(echo "$RESULT" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE=$(echo "$RESULT" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE"
if [ "$HTTP_CODE" = "200" ]; then 
  echo "Result: [PASS]"
  TEST4="PASS"
else 
  echo "Result: [FAIL]"
  TEST4="FAIL"
fi
echo ""

# Test 5: HIPAA Compliance
echo "======================================================================"
echo "[Step 6/6] TEST 5: HIPAA Compliance - Log PHI Access"
echo "======================================================================"
RESULT=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SUPABASE_URL}/functions/v1/hipaa-compliance" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"action\":\"log_access\",\"patient_id\":\"${USER_ID}\",\"phi_type\":\"prescription\",\"access_type\":\"view\",\"reason\":\"Testing PHI access logging for security audit\"}")
  
HTTP_CODE=$(echo "$RESULT" | grep "HTTP_STATUS" | cut -d':' -f2)
RESPONSE=$(echo "$RESULT" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $RESPONSE"
if [ "$HTTP_CODE" = "200" ]; then 
  echo "Result: [PASS]"
  TEST5="PASS"
else 
  echo "Result: [FAIL]"
  TEST5="FAIL"
fi
echo ""

# Summary
echo "======================================================================"
echo "TEST SUMMARY - SECURITY EDGE FUNCTIONS"
echo "======================================================================"
echo "1. Rate Limiting:       [$TEST1]"
echo "2. 2FA Management:      [$TEST2]"
echo "3. Threat Detection:    [$TEST3]"
echo "4. GDPR Compliance:     [$TEST4]"
echo "5. HIPAA Compliance:    [$TEST5]"
echo "======================================================================"
