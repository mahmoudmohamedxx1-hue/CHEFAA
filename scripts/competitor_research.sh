#!/bin/bash
# Competitor research for The Pharmacy - Egyptian online pharmacy market
mkdir -p /home/z/my-project/scripts/research-results
cd /home/z/my-project/scripts/research-results

run_search() {
  local name="$1"
  local query="$2"
  local num="${3:-10}"
  echo "--- Searching: $name"
  z-ai function -n web_search -a "{\"query\": \"$query\", \"num\": $num}" -o "${name}.json" 2>/dev/null || echo "FAILED: $name"
}

# Core competitors
run_search "chefaa_main" "Chefaa Egypt online pharmacy app features delivery" 10
run_search "chefaa_business" "Chefaa Egypt funding startup valuation growth" 10
run_search "app_19011" "19011 Egypt online pharmacy app services delivery" 10
run_search "el_ezaby" "El Ezaby pharmacy Egypt online shopping app" 10
run_search "seif_pharmacy" "Seif pharmacy Egypt online delivery app" 10
run_search "yodawy" "Yodawy Egypt pharmacy startup digital" 10

# Market landscape
run_search "market_egypt" "Egypt online pharmacy e-commerce market size growth 2025" 10
run_search "best_apps" "best online pharmacy apps Egypt 2025 comparison" 10
run_search "vezeeta_pharmacy" "Vezeeta pharmacy delivery Egypt" 10
run_search "competition_intl" "online pharmacy competitive landscape Middle East North Africa MENA" 10

echo "=== DONE ==="
ls -la /home/z/my-project/scripts/research-results/
