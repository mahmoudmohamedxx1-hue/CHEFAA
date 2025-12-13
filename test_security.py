import requests
import json

SUPABASE_URL = "https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

print("=" * 60)
print("SECURITY EDGE FUNCTIONS - COMPREHENSIVE TEST SUITE")
print("=" * 60)
print()

# Step 1: Authenticate
print("Step 1: Authenticating test user...")
email = "security-test@chefaa.com"
password = "SecureTest123!"

# Try sign in
try:
    response = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"Content-Type": "application/json", "apikey": ANON_KEY},
        json={"email": email, "password": password}
    )
    data = response.json()
    
    if "access_token" not in data:
        print("User not found, creating new account...")
        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={"Content-Type": "application/json", "apikey": ANON_KEY},
            json={"email": email, "password": password}
        )
        data = response.json()
    
    if "access_token" in data:
        token = data["access_token"]
        user_id = data.get("user", {}).get("id")
        print(f"Authenticated successfully")
        print(f"User ID: {user_id}")
        print()
    else:
        print(f"Authentication failed: {data}")
        exit(1)
except Exception as e:
    print(f"Error during authentication: {e}")
    exit(1)

# Test results
results = []

# Test 1: Rate Limiting
print("-" * 60)
print("TEST 1: Rate Limiting")
print("-" * 60)
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
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    results.append(("Rate Limiting", response.status_code == 200))
except Exception as e:
    print(f"Error: {e}")
    results.append(("Rate Limiting", False))
print()

# Test 2: 2FA Management
print("-" * 60)
print("TEST 2: 2FA Management - Setup TOTP")
print("-" * 60)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/2fa-management",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={"action": "setup_totp"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    results.append(("2FA Management", response.status_code == 200))
except Exception as e:
    print(f"Error: {e}")
    results.append(("2FA Management", False))
print()

# Test 3: Threat Detection
print("-" * 60)
print("TEST 3: Threat Detection")
print("-" * 60)
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
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    results.append(("Threat Detection", response.status_code == 200))
except Exception as e:
    print(f"Error: {e}")
    results.append(("Threat Detection", False))
print()

# Test 4: GDPR Compliance
print("-" * 60)
print("TEST 4: GDPR Compliance - Data Access Request")
print("-" * 60)
try:
    response = requests.post(
        f"{SUPABASE_URL}/functions/v1/gdpr-compliance",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "apikey": ANON_KEY
        },
        json={"action": "request_data"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    results.append(("GDPR Compliance", response.status_code == 200))
except Exception as e:
    print(f"Error: {e}")
    results.append(("GDPR Compliance", False))
print()

# Test 5: HIPAA Compliance
print("-" * 60)
print("TEST 5: HIPAA Compliance - Log PHI Access")
print("-" * 60)
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
            "reason": "Testing PHI access logging"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    results.append(("HIPAA Compliance", response.status_code == 200))
except Exception as e:
    print(f"Error: {e}")
    results.append(("HIPAA Compliance", False))
print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
passed = sum(1 for _, success in results if success)
failed = len(results) - passed

for i, (name, success) in enumerate(results, 1):
    status = "PASS" if success else "FAIL"
    print(f"{i}. {name}: {status}")

print(f"\nTotal: {len(results)} tests")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
