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

  echo "=== Origin selected logo and favicon ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$LOGO" -o "$TMP/logo.png"
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$FAVICON" -o "$TMP/favicon.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-logo.png" "$TMP/logo.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-favicon.png" "$TMP/favicon.png"

  echo "=== Public Cloudflare HTTPS GET checks ==="
  for route in / /login /api/method/ping "$CSS" "$LOGO" "$FAVICON"; do
    status="$(curl -fsSL --connect-timeout 5 --max-time 20 \
      -o /dev/null -w '%{http_code}' "https://$SITE$route")" || {
        echo "STOP: public route failed: $route"; exit 4;
      }
    echo "$status $route"
  done
  echo "PASS: public routes, homepage stylesheet, original PNG and favicon"
)
