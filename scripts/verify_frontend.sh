#!/usr/bin/env bash
# Read-only checks. Insecure TLS is limited to explicit localhost origin testing.
(
  set -Eeuo pipefail
  trap 'echo "FRONTEND CHECK FAILED at line $LINENO" >&2' ERR
  SITE="erp-developers.com"
  BENCH="${BENCH:-/data/frappe/frappe-bench}"
  APP="$BENCH/apps/erpdevelopers"
  test -f "$BENCH/sites/$SITE/site_config.json"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  origin() {
    curl -kfsSL --connect-timeout 5 --max-time 20 \
      --resolve "$SITE:443:127.0.0.1" "https://$SITE$2" -o "$TMP/$1"
  }
  DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/brand.css" | cut -c1-16)"
  CSS="/assets/erpdevelopers/css/brand.css?v=$DIGEST"
  LOGIN_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/login.css" | cut -c1-16)"
  LOGIN_CSS="/assets/erpdevelopers/css/login.css?v=$LOGIN_DIGEST"
  ARABIC_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/arabic_typography.css" | cut -c1-16)"
  ARABIC_CSS="/assets/erpdevelopers/css/arabic_typography.css?v=$ARABIC_DIGEST"
  PORTAL_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/portal.css" | cut -c1-16)"
  PORTAL_CSS="/assets/erpdevelopers/css/portal.css?v=$PORTAL_DIGEST"
  MEETING_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/meeting.css" | cut -c1-16)"
  MEETING_CSS="/assets/erpdevelopers/css/meeting.css?v=$MEETING_DIGEST"
  EVENTS_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/events.css" | cut -c1-16)"
  EVENTS_CSS="/assets/erpdevelopers/css/events.css?v=$EVENTS_DIGEST"
  CATALOG_DIGEST="$(sha256sum "$APP/erpdevelopers/public/js/catalog.js" | cut -c1-16)"
  CATALOG_JS="/assets/erpdevelopers/js/catalog.js?v=$CATALOG_DIGEST"
  LANGUAGE_DIGEST="$(sha256sum "$APP/erpdevelopers/public/js/language.js" | cut -c1-16)"
  LANGUAGE_JS="/assets/erpdevelopers/js/language.js?v=$LANGUAGE_DIGEST"
  LOGO="/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
  FAVICON="/assets/erpdevelopers/images/erpdevelopers-selected-favicon.png"

  echo "=== Origin homepage: CSS and SEO ==="
  origin home.html /
  grep -Fq "href=\"$CSS\"" "$TMP/home.html" || { echo "STOP: stale homepage CSS reference"; exit 3; }
  origin brand.css "$CSS"
  cmp -s "$APP/erpdevelopers/public/css/brand.css" "$TMP/brand.css" || { echo "STOP: stale brand CSS bytes"; exit 3; }
  grep -Fq 'rel="canonical" href="https://erp-developers.com/"' "$TMP/home.html" || { echo "STOP: missing canonical homepage URL"; exit 3; }
  "$BENCH/env/bin/python" "$APP/scripts/inspect_home_metadata.py" "$TMP/home.html"
  grep -Fq '"@type":"Organization"' "$TMP/home.html" || { echo "STOP: missing Organization JSON-LD"; exit 3; }
  origin sitemap.xml /sitemap.xml
  grep -Fq '<urlset' "$TMP/sitemap.xml"
  CARD_COUNT="$(grep -o 'class="ed-tile"' "$TMP/home.html" | wc -l | tr -d '[:space:]')"
  test "$CARD_COUNT" = "6"

  echo "=== Native EN/AR language rendering ==="
  origin home-en.html '/erp-developers-home?_lang=en'
  origin home-ar.html '/erp-developers-home?_lang=ar'
  grep -Fq 'Developer Hub' "$TMP/home-en.html"
  grep -Fq 'Learning Academy' "$TMP/home-en.html"
  grep -Fq 'Team Login' "$TMP/home-en.html"
  grep -Fq 'بوابة المطورين' "$TMP/home-ar.html"
  grep -Fq 'أكاديمية التعلم' "$TMP/home-ar.html"

  echo "=== Public Hub routes, including Events ==="
  for entry in 'training:ed-training-title' 'events:ed-events-title' 'insights:ed-insights-title' 'lets-talk:ed-meet-title' 'privacy:ed-privacy-title'; do
    route="${entry%%:*}"
    marker="${entry#*:}"
    origin "$route.html" "/$route?_lang=en"
    grep -Fq "id=\"$marker\"" "$TMP/$route.html" || { echo "STOP: route did not render: $route"; exit 3; }
    grep -Fq 'href="/training"' "$TMP/$route.html"
    grep -Fq 'href="/events"' "$TMP/$route.html"
  done
  origin events-ar.html '/events?_lang=ar'
  grep -Fq 'دليل الفعاليات' "$TMP/events-ar.html" || { echo "STOP: compiled Arabic event translations missing"; exit 3; }
  grep -Fq "href=\"$EVENTS_CSS\"" "$TMP/events.html"
  origin events.css "$EVENTS_CSS"
  cmp -s "$APP/erpdevelopers/public/css/events.css" "$TMP/events.css"

  echo "=== Meeting readiness and assets ==="
  for marker in book-meeting ed-meeting-form ed-meeting-slots; do
    grep -Fq "id=\"$marker\"" "$TMP/lets-talk.html"
  done
  grep -Fq 'Your meeting is confirmed after you verify it.' "$TMP/lets-talk.html"
  if grep -Fq 'data-booking-ready="0"' "$TMP/lets-talk.html"; then
    grep -Fq 'ed-meet-offline-notice' "$TMP/lets-talk.html"
    grep -Fq '<fieldset class="ed-meet-fields" disabled' "$TMP/lets-talk.html"
  else
    grep -Fq 'data-booking-ready="1"' "$TMP/lets-talk.html"
  fi
  grep -Fq "href=\"$MEETING_CSS\"" "$TMP/lets-talk.html"
  origin meeting.css "$MEETING_CSS"
  cmp -s "$APP/erpdevelopers/public/css/meeting.css" "$TMP/meeting.css"

  echo "=== Training script delivery and in-page-only controls ==="
  grep -Fq "href=\"$PORTAL_CSS\"" "$TMP/training.html"
  grep -Fq "src=\"$CATALOG_JS\"" "$TMP/training.html" || { echo "STOP: stale catalog script reference"; exit 3; }
  origin catalog.js "$CATALOG_JS"
  cmp -s "$APP/erpdevelopers/public/js/catalog.js" "$TMP/catalog.js"
  "$BENCH/env/bin/python" "$APP/scripts/inspect_training_player.py" "$TMP/training.html"
  origin portal.css "$PORTAL_CSS"
  cmp -s "$APP/erpdevelopers/public/css/portal.css" "$TMP/portal.css"

  echo "=== Native login, Arabic typography and Desk sign-in ==="
  origin login.html '/login?_lang=en'
  grep -Fq 'id="page-login"' "$TMP/login.html"
  grep -Fq 'for-login' "$TMP/login.html"
  grep -Fq 'id="language-switcher"' "$TMP/login.html"
  for rendered in home-ar training events login; do
    grep -Fq "href=\"$ARABIC_CSS\"" "$TMP/$rendered.html" || { echo "STOP: missing Arabic CSS; reload web workers"; exit 3; }
  done
  origin arabic.css "$ARABIC_CSS"
  cmp -s "$APP/erpdevelopers/public/css/arabic_typography.css" "$TMP/arabic.css"
  grep -Fq 'family=Tajawal' "$TMP/arabic.css"
  SIGNIN_HREF="/login?redirect-to=/desk"
  SIGNIN_COUNT="$(grep -oF 'href="'$SIGNIN_HREF'"' "$TMP/home.html" | wc -l | tr -d '[:space:]')"
  test "$SIGNIN_COUNT" = "2"
  origin login-desk.html "$SIGNIN_HREF"
  grep -Fq 'id="page-login"' "$TMP/login-desk.html"
  for SETTINGS in 'Website Settings' 'Navbar Settings'; do
    ACTUAL_LOGO="$(cd "$BENCH" && bench --site "$SITE" execute frappe.db.get_single_value --args "[\"$SETTINGS\",\"app_logo\"]")"
    test "$ACTUAL_LOGO" = "$LOGO" || { echo "STOP: stored logo mismatch for $SETTINGS"; exit 3; }
  done
  grep -Fq "$LOGIN_CSS" "$TMP/login.html"
  "$BENCH/env/bin/python" "$APP/scripts/inspect_login_brand.py" "$TMP/login.html" --site "$SITE" --check-language
  grep -Fq "src=\"$LANGUAGE_JS\"" "$TMP/login.html"
  origin language.js "$LANGUAGE_JS"
  cmp -s "$APP/erpdevelopers/public/js/language.js" "$TMP/language.js"
  if grep -Fq 'login_chrome.js' "$TMP/login.html"; then echo "STOP: stale login injection script"; exit 3; fi
  origin login.css "$LOGIN_CSS"
  cmp -s "$APP/erpdevelopers/public/css/login.css" "$TMP/login.css"
  origin logo.png "$LOGO"
  origin favicon.png "$FAVICON"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-logo.png" "$TMP/logo.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-favicon.png" "$TMP/favicon.png"

  echo "=== Public Cloudflare HTTPS GET checks ==="
  for route in / /training /events /insights /lets-talk /privacy /login /api/method/ping "$CSS" "$LOGIN_CSS" "$ARABIC_CSS" "$PORTAL_CSS" "$MEETING_CSS" "$EVENTS_CSS" "$CATALOG_JS" "$LOGO" "$FAVICON"; do
    status="$(curl -fsSL --connect-timeout 5 --max-time 20 -o /dev/null -w '%{http_code}' "https://$SITE$route")" || { echo "STOP: public route failed: $route"; exit 4; }
    echo "$status $route"
  done
  echo "PASS: public routes, Events, EN/AR, metadata, native login, in-page player and asset bytes"
)
