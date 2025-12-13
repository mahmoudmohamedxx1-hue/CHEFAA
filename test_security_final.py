import requests
import json
import sys

SUPABASE_URL = "https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

print("=" * 70)
print("SECURITY EDGE FUNCTIONS - COMPREHENSIVE TEST SUITE")
print("=" * 70)
print()

# Step 1: Authenticate with existing test account
print("Step 1: Authenticating with test account...")
email = "ntqtcbqk@minimax.com"  # Existing test account
password = "zKhtFq0dHz"

try:
    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"Content-Type": "application/json", "apikey": ANON_KEY},
        json={"email": email, "password": password},
        timeout=10
    )
    data = response.json()
    
    if "access_token" in data:
        token = data["access_token"]
        user_id = data.get("user", {}).get("id")
        print(f"[SUCCESS] Authenticated successfully")
        print(f"  User ID: {user_id}")
        print(f"  Email: {email}")
        print()
    else:
        print(f"[FAILED] Authentication failed")
        print(f"  Response: {json.dumps(data, indent=2)}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Authentication error: {e}")
    sys.exit(1)

# Test results
results = []

# Test 1: Rate Limiting
print("=" * 70)
print("TEST 1: Rate Limiting - Check Request Limits")
print("=" * 70)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/rate-limiting",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={
            "action": "check",
            "endpoint": "/api/products",
            "identifier": user_id,
            "type": "user"
        },
        timeout=10
    )
    resp_json = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(resp_json, indent=2))
    
    success = response.status_code == 200 and resp_json.get("allowed") is not None
    results.append(("Rate Limiting", success, response.status_code))
    print(f"\nResult: {'[PASS]' if success else '[FAIL]'}")
except Exception as e:
    print(f"[ERROR] {e}")
    results.append(("Rate Limiting", False, "error"))
print()

# Test 2: 2FA Management - Setup TOTP
print("=" * 70)
print("TEST 2: 2FA Management - Setup TOTP")
print("=" * 70)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/2fa-management",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={"action": "setup_totp"},
        timeout=10
    )
    resp_json = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(resp_json, indent=2))
    
    success = response.status_code == 200 and ("secret" in resp_json or "success" in resp_json)
    results.append(("2FA Management", success, response.status_code))
    print(f"\nResult: {'[PASS]' if success else '[FAIL]'}")
except Exception as e:
    print(f"[ERROR] {e}")
    results.append(("2FA Management", False, "error"))
print()

# Test 3: Threat Detection - Analyze Login Behavior
print("=" * 70)
print("TEST 3: Threat Detection - Analyze Login Behavior")
print("=" * 70)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/threat-detection",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={
            "action": "analyze",
            "user_id": user_id,
            "event_type": "login",
            "ip_address": "192.168.1.100",
            "location": "Cairo, Egypt",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        timeout=10
    )
    resp_json = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(resp_json, indent=2))
    
    success = response.status_code == 200 and ("anomaly_score" in resp_json or "success" in resp_json)
    results.append(("Threat Detection", success, response.status_code))
    print(f"\nResult: {'[PASS]' if success else '[FAIL]'}")
except Exception as e:
    print(f"[ERROR] {e}")
    results.append(("Threat Detection", False, "error"))
print()

# Test 4: GDPR Compliance - Data Access Request
print("=" * 70)
print("TEST 4: GDPR Compliance - Data Access Request")
print("=" * 70)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/gdpr-compliance",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={"action": "request_data"},
        timeout=10
    )
    resp_json = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(resp_json, indent=2))
    
    success = response.status_code == 200 and ("data" in resp_json or "request_id" in resp_json or "success" in resp_json)
    results.append(("GDPR Compliance", success, response.status_code))
    print(f"\nResult: {'[PASS]' if success else '[FAIL]'}")
except Exception as e:
    print(f"[ERROR] {e}")
    results.append(("GDPR Compliance", False, "error"))
print()

# Test 5: HIPAA Compliance - Log PHI Access
print("=" * 70)
print("TEST 5: HIPAA Compliance - Log PHI Access")
print("=" * 70)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/hipaa-compliance",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={
            "action": "log_access",
            "patient_id": user_id,
            "phi_type": "prescription",
            "access_type": "view",
            "reason": "Testing PHI access logging for security audit"
        },
        timeout=10
    )
    resp_json = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(resp_json, indent=2))
    
    success = response.status_code == 200 and ("audit_id" in resp_json or "success" in resp_json)
    results.append(("HIPAA Compliance", success, response.status_code))
    print(f"\nResult: {'[PASS]' if success else '[FAIL]'}")
except Exception as e:
    print(f"[ERROR] {e}")
    results.append(("HIPAA Compliance", False, "error"))
print()

# Test Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
passed = sum(1 for _, success, _ in results if success)
failed = len(results) - passed

for i, (name, success, status) in enumerate(results, 1):
    status_icon = "[PASS]" if success else "[FAIL]"
    print(f"{i}. {name:25s} {status_icon:8s} (HTTP {status})")

print()
print(f"Total Tests:   {len(results)}")
print(f"Passed:        {passed} tests")
print(f"Failed:        {failed} tests")
print(f"Success Rate:  {(passed / len(results) * 100):.1f}%")

if passed == len(results):
    print("\n[SUCCESS] All security edge functions are working correctly!")
elif passed > 0:
    print(f"\n[PARTIAL] {passed} out of {len(results)} functions working")
else:
    print("\n[CRITICAL] All security functions failed - requires immediate attention")

print("=" * 70)
