#!/usr/bin/env bash
# Read-only frontend check. Direct-origin TLS bypass applies ONLY to localhost tests.
(
  set -Eeuo pipefail
  trap 'echo "FRONTEND CHECK FAILED at line $LINENO" >&2' ERR
  SITE="erp-developers.com"
  BENCH="${BENCH:-/data/frappe/frappe-bench}"
  APP="$BENCH/apps/erpdevelopers"
  test -f "$BENCH/sites/$SITE/site_config.json"
  test -f "$APP/erpdevelopers/public/css/brand.css"

  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/brand.css" | cut -c1-16)"
  CSS="/assets/erpdevelopers/css/brand.css?v=$DIGEST"
  LOGO="/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
  FAVICON="/assets/erpdevelopers/images/erpdevelopers-selected-favicon.png"

  echo "=== Origin homepage: stylesheet URL and real CSS bytes ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE/" -o "$TMP/home.html"
  grep -Fq "href=\"$CSS\"" "$TMP/home.html" || {
    echo "STOP: homepage missing $CSS; check page context, caches, web worker restart"; exit 3;
  }
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$CSS" -o "$TMP/brand.css"
  grep -Fq '.ed-hero-inner' "$TMP/brand.css"
  cmp -s "$APP/erpdevelopers/public/css/brand.css" "$TMP/brand.css" || {
    echo "STOP: CSS served by origin differs from deployed file"; exit 3;
  }

  echo "=== Confirm data-driven homepage content rendered ==="
  CARD_COUNT="$(grep -o 'class="ed-tile"' "$TMP/home.html" | wc -l | tr -d '[:space:]')"
  test "$CARD_COUNT" = "6" || {
    echo "STOP: expected six ecosystem cards but rendered $CARD_COUNT"; exit 3;
  }
  echo "=== Verify English and Arabic using Frappe's native _lang request ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE/erp-developers-home?_lang=en" -o "$TMP/home-en.html"
  grep -Fq 'Developer Hub' "$TMP/home-en.html"
  grep -Fq 'Learning Academy' "$TMP/home-en.html"
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE/erp-developers-home?_lang=ar" -o "$TMP/home-ar.html"
  grep -Fq 'بوابة المطورين' "$TMP/home-ar.html" || {
    echo "STOP: missing Arabic homepage translation"; exit 3;
  }
  grep -Fq 'أكاديمية التعلم' "$TMP/home-ar.html"

  echo "=== Confirm native Frappe login and language picker render ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE/login?_lang=en" -o "$TMP/login.html"
  grep -Fq 'id="page-login"' "$TMP/login.html"
  grep -Fq 'for-login' "$TMP/login.html"
  grep -Fq 'id="language-switcher"' "$TMP/login.html"

  echo "=== Origin selected logo and favicon ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$LOGO" -o "$TMP/logo.png"
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$FAVICON" -o "$TMP/favicon.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-logo.png" "$TMP/logo.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-favicon.png" "$TMP/favicon.png"

  echo "=== Public Cloudflare HTTPS GET checks ==="
  for route in / /login /api/method/ping "$CSS" "$LOGO" "$FAVICON" /assets/erpdevelopers/css/login.css /assets/erpdevelopers/js/login_chrome.js; do
    status="$(curl -fsSL --connect-timeout 5 --max-time 20 \
      -o /dev/null -w '%{http_code}' "https://$SITE$route")" || {
        echo "STOP: public route failed: $route"; exit 4;
      }
    echo "$status $route"
  done
  echo "PASS: EN/AR translation, native login, CSS, approved PNG and public routes"
)
