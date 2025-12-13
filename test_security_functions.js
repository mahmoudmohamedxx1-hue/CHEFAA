const SUPABASE_URL = "https://hdcpruwkvarfbdtztzgq.supabase.co";
const ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkY3BydXdrdmFyZmJkdHp0emdxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5MzEyMzIsImV4cCI6MjA3NzUwNzIzMn0.lq3E94nj3GrQtkJ-LfQtOBvTptFgOjPJDiMZ7csXnOQ";

// Create or sign in a test user
async function getAuthToken() {
  const email = 'security-test@chefaa.com';
  const password = 'SecureTest123!';
  
  console.log('Creating/signing in test user...');
  
  // Try to sign in first
  let response = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': ANON_KEY
    },
    body: JSON.stringify({ email, password })
  });
  
  let data = await response.json();
  
  // If sign in fails, try to sign up
  if (!data.access_token) {
    console.log('User not found, creating new account...');
    response = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': ANON_KEY
      },
      body: JSON.stringify({ email, password })
    });
    data = await response.json();
  }
  
  if (data.access_token) {
    console.log('Authentication successful');
    console.log(`User ID: ${data.user?.id}`);
    return { token: data.access_token, userId: data.user?.id };
  } else {
    console.log('Authentication failed:', data);
    return null;
  }
}

async function testFunction(name, endpoint, data, authToken) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Testing: ${name}`);
  console.log(`${'='.repeat(60)}`);
  
  try {
    const response = await fetch(`${SUPABASE_URL}/functions/v1/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
        'apikey': ANON_KEY
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    console.log(`Status: ${response.status} ${response.ok ? 'PASS' : 'FAIL'}`);
    console.log(`Response:`, JSON.stringify(result, null, 2));
    return { status: response.status, ok: response.ok, data: result };
  } catch (error) {
    console.log(`Error:`, error.message);
    return { status: 'error', ok: false, error: error.message };
  }
}

async function runSecurityTests() {
  console.log('\n' + '='.repeat(60));
  console.log('SECURITY EDGE FUNCTIONS - COMPREHENSIVE TEST SUITE');
  console.log('='.repeat(60));
  
  // Step 1: Authenticate
  const auth = await getAuthToken();
  if (!auth) {
    console.log('\nCannot proceed without authentication');
    return;
  }
  
  const { token, userId } = auth;
  const results = [];
  
  // Test 1: Rate Limiting (no auth required)
  const r1 = await testFunction(
    '1. Rate Limiting - Check Limit',
    'rate-limiting',
    {
      action: 'check',
      endpoint: '/api/products',
      identifier: userId,
      type: 'user'
    },
    token
  );
  results.push({ name: 'Rate Limiting', ...r1 });
  
  // Test 2: 2FA Management - Setup TOTP
  const r2 = await testFunction(
    '2. 2FA Management - Setup TOTP',
    '2fa-management',
    {
      action: 'setup_totp'
    },
    token
  );
  results.push({ name: '2FA Management', ...r2 });
  
  // Test 3: Threat Detection - Analyze Behavior
  const r3 = await testFunction(
    '3. Threat Detection - Analyze Login',
    'threat-detection',
    {
      action: 'analyze',
      user_id: userId,
      event_type: 'login',
      ip_address: '192.168.1.100',
      location: 'Cairo, Egypt',
      user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    token
  );
  results.push({ name: 'Threat Detection', ...r3 });
  
  // Test 4: GDPR Compliance - Request Data
  const r4 = await testFunction(
    '4. GDPR Compliance - Data Access Request',
    'gdpr-compliance',
    {
      action: 'request_data'
    },
    token
  );
  results.push({ name: 'GDPR Compliance', ...r4 });
  
  // Test 5: HIPAA Compliance - Log PHI Access
  const r5 = await testFunction(
    '5. HIPAA Compliance - Log PHI Access',
    'hipaa-compliance',
    {
      action: 'log_access',
      patient_id: userId,
      phi_type: 'prescription',
      access_type: 'view',
      reason: 'Processing prescription order for testing'
    },
    token
  );
  results.push({ name: 'HIPAA Compliance', ...r5 });
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));
  
  const passed = results.filter(r => r.ok).length;
  const failed = results.filter(r => !r.ok).length;
  
  results.forEach((r, i) => {
    console.log(`${i + 1}. ${r.name}: ${r.ok ? 'PASS' : 'FAIL'} (${r.status})`);
  });
  
  console.log(`\nTotal: ${results.length} tests`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Success Rate: ${((passed / results.length) * 100).toFixed(1)}%`);
}

runSecurityTests().catch(console.error);
