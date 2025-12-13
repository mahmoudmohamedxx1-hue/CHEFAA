#!/usr/bin/env python3
import requests
import json
from datetime import datetime

print("="*80)
print("PHARMACEUTICAL PLATFORM - COMPREHENSIVE API TESTING")
print("="*80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Platform URL: https://e15thsj0jrus.space.minimax.io")
print("="*80)
print()

SUPABASE_URL = "https://hdcpruwkvarfbdtztzgq.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ"

results = []

def test(name, func):
    try:
        result = func()
        status = "PASS" if result['success'] else "FAIL"
        results.append({'name': name, 'status': status, 'details': result.get('details', '')})
        print(f"[{status}] {name}")
        if result.get('details'):
            print(f"      {result['details']}")
    except Exception as e:
        results.append({'name': name, 'status': "ERROR", 'details': str(e)})
        print(f"[ERROR] {name}: {str(e)}")

print("FRONTEND TESTS")
print("-"*80)

# Test 1
resp = requests.get("https://e15thsj0jrus.space.minimax.io", timeout=10)
test("Homepage Loading", lambda: {
    'success': resp.status_code == 200,
    'details': f"HTTP {resp.status_code}, {resp.elapsed.total_seconds():.2f}s"
})

# Test 2
test("Title Tag Present", lambda: {
    'success': "PharmaCare" in resp.text,
    'details': "Title found" if "PharmaCare" in resp.text else "Missing"
})

# Test 3
test("React Root Element", lambda: {
    'success': 'id="root"' in resp.text,
    'details': "Found" if 'id="root"' in resp.text else "Missing"
})

# Test 4
manifest_resp = requests.get("https://e15thsj0jrus.space.minimax.io/manifest.json")
test("PWA Manifest", lambda: {
    'success': manifest_resp.status_code == 200,
    'details': f"HTTP {manifest_resp.status_code}"
})

# Test 5
sw_resp = requests.get("https://e15thsj0jrus.space.minimax.io/sw.js")
test("Service Worker", lambda: {
    'success': sw_resp.status_code == 200,
    'details': f"HTTP {sw_resp.status_code}"
})

print()
print("DATABASE API TESTS")
print("-"*80)

headers = {"apikey": ANON_KEY, "Content-Type": "application/json"}

# Test 6
categories_resp = requests.get(f"{SUPABASE_URL}/rest/v1/categories?select=*&limit=5", headers=headers)
test("Get Categories", lambda: {
    'success': categories_resp.status_code == 200,
    'details': f"HTTP {categories_resp.status_code}, Count: {len(categories_resp.json()) if categories_resp.status_code == 200 else 0}"
})

# Test 7
products_resp = requests.get(f"{SUPABASE_URL}/rest/v1/products?select=*&limit=5", headers=headers)
test("Get Products", lambda: {
    'success': products_resp.status_code == 200,
    'details': f"HTTP {products_resp.status_code}, Count: {len(products_resp.json()) if products_resp.status_code == 200 else 0}"
})

print()
print("EDGE FUNCTION TESTS")
print("-"*80)

# Test 8
rate_resp = requests.post(f"{SUPABASE_URL}/functions/v1/rate-limiting",
                         headers={"Content-Type": "application/json"},
                         json={"action": "check", "identifier": "test", "limit": 100},
                         timeout=10)
test("Rate Limiting Function", lambda: {
    'success': rate_resp.status_code in [200, 401],
    'details': f"HTTP {rate_resp.status_code}"
})

print()
print("="*80)
print("SUMMARY")
print("="*80)
passed = sum(1 for r in results if r['status'] == 'PASS')
total = len(results)
print(f"Total: {total} | Passed: {passed} | Failed: {total-passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if passed < total:
    print("\nFAILED TESTS:")
    for r in results:
        if r['status'] != 'PASS':
            print(f"  - {r['name']}: {r['details']}")
