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
  LOGIN_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/login.css" | cut -c1-16)"
  LOGIN_CSS="/assets/erpdevelopers/css/login.css?v=$LOGIN_DIGEST"

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

  echo "=== SEO: canonical homepage, Frappe meta, structured data and sitemap ==="
  grep -Fq 'rel="canonical" href="https://erp-developers.com/"' "$TMP/home.html" || {
    echo "STOP: canonical homepage URL missing"; exit 3;
  }
  grep -Fq 'property="og:type" content="website"' "$TMP/home.html" || {
    echo "STOP: OpenGraph website metadata missing"; exit 3;
  }
  grep -Fq '"@type":"Organization"' "$TMP/home.html" || {
    echo "STOP: Organization JSON-LD missing"; exit 3;
  }
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE/sitemap.xml" -o "$TMP/sitemap.xml"
  grep -Fq '<urlset' "$TMP/sitemap.xml" || {
    echo "STOP: Frappe sitemap XML is missing"; exit 3;
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

  echo "=== Public Hub: Team Login, training, insights, consultation and privacy ==="
  grep -Fq "Team Login" "$TMP/home-en.html" || {
    echo "STOP: Team Login label not rendered"; exit 3;
  }
  for entry in "training:ed-training-title" "insights:ed-insights-title" \
               "lets-talk:ed-meet-title" "privacy:ed-privacy-title"; do
    route="${entry%%:*}"
    marker="${entry#*:}"
    curl -kfsSL --connect-timeout 5 --max-time 20 \
      --resolve "$SITE:443:127.0.0.1" \
      "https://$SITE/$route?_lang=en" -o "$TMP/$route.html"
    grep -Fq "id=\"$marker\"" "$TMP/$route.html" || {
      echo "STOP: public hub page $route did not render correctly"; exit 3;
    }
    grep -Fq 'href="/training"' "$TMP/$route.html" || {
      echo "STOP: shared hub navigation missing from $route"; exit 3;
    }
  done
  grep -Fq 'id="book-meeting"' "$TMP/lets-talk.html" || {
    echo "STOP: meeting scheduler container missing"; exit 3;
  }
  if grep -Fq 'id="ed-meeting-form"' "$TMP/lets-talk.html"; then
    grep -Fq "Your meeting is confirmed after you verify it." "$TMP/lets-talk.html" || {
      echo "STOP: native booking email confirmation copy missing"; exit 3;
    }
  else
    grep -Fq 'ed-meeting-unavailable' "$TMP/lets-talk.html" || {
      echo "STOP: meeting booking must fail closed when calendar is unconfigured"; exit 3;
    }
  fi
  echo "=== Verify native booking assets and page without leaking appointment data ==="
  MEETING_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/meeting.css" | cut -c1-16)"
  MEETING_CSS="/assets/erpdevelopers/css/meeting.css?v=$MEETING_DIGEST"
  grep -Fq "href=\"$MEETING_CSS\"" "$TMP/lets-talk.html" || {
    echo "STOP: meeting CSS fingerprint missing"; exit 3;
  }
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$MEETING_CSS" -o "$TMP/meeting.css"
  cmp -s "$APP/erpdevelopers/public/css/meeting.css" "$TMP/meeting.css" || {
    echo "STOP: meeting CSS differs from installed file"; exit 3;
  }
  PORTAL_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/portal.css" | cut -c1-16)"
  PORTAL_CSS="/assets/erpdevelopers/css/portal.css?v=$PORTAL_DIGEST"
  grep -Fq "href=\"$PORTAL_CSS\"" "$TMP/training.html" || {
    echo "STOP: public hub CSS fingerprint missing"; exit 3;
  }
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$PORTAL_CSS" -o "$TMP/portal.css"
  cmp -s "$APP/erpdevelopers/public/css/portal.css" "$TMP/portal.css" || {
    echo "STOP: public hub CSS bytes differ from the installed app"; exit 3;
  }
  echo "=== Confirm native Frappe login and language picker render ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE/login?_lang=en" -o "$TMP/login.html"
  grep -Fq 'id="page-login"' "$TMP/login.html"
  grep -Fq 'for-login' "$TMP/login.html"
  grep -Fq 'id="language-switcher"' "$TMP/login.html"

  echo "=== Verify explicit Desk sign-in intent in public homepage ==="
  SIGNIN_HREF="/login?redirect-to=/desk"
  SIGNIN_COUNT="$(grep -oF 'href="'$SIGNIN_HREF'"' "$TMP/home.html" | wc -l | tr -d '[:space:]')"
  test "$SIGNIN_COUNT" = "2" || {
    echo "STOP: Desk sign-in links must explicitly request /desk"; exit 3;
  }
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE$SIGNIN_HREF" -o "$TMP/login-desk.html"
  grep -Fq 'id="page-login"' "$TMP/login-desk.html"

  echo "=== Confirm public/login and Desk use the same approved PNG ==="
  for SETTINGS in "Website Settings" "Navbar Settings"; do
    ACTUAL_LOGO="$(cd "$BENCH" && bench --site "$SITE" execute \
      frappe.db.get_single_value --args "[\"$SETTINGS\",\"app_logo\"]")"
    if [ "$ACTUAL_LOGO" != "$LOGO" ]; then
      echo "STOP: $SETTINGS.app_logo is $ACTUAL_LOGO, not the approved PNG"
      exit 3
    fi
    echo "PASS: $SETTINGS.app_logo"
  done

  echo "=== First-paint login CSS and approved navbar logo ==="
  grep -Fq "$LOGIN_CSS" "$TMP/login.html" || {
    echo "STOP: fingerprinted login CSS not linked"; exit 3;
  }
  # Parse the actual <a class="navbar-brand"> image structurally.
  # Exact "<img src=..." grep incorrectly rejects valid attributes/quotes.
  "$BENCH/env/bin/python" "$APP/scripts/inspect_login_brand.py" "$TMP/login.html" \
    --site "$SITE"
  if grep -Fq 'login_chrome.js' "$TMP/login.html"; then
    echo "STOP: stale script still reinserts the login layout"; exit 3;
  fi
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" \
    "https://$SITE$LOGIN_CSS" -o "$TMP/login.css"
  cmp -s "$APP/erpdevelopers/public/css/login.css" "$TMP/login.css" || {
    echo "STOP: native login CSS does not match deployed file"; exit 3;
  }

  echo "=== Origin selected logo and favicon ==="
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$LOGO" -o "$TMP/logo.png"
  curl -kfsSL --connect-timeout 5 --max-time 20 \
    --resolve "$SITE:443:127.0.0.1" "https://$SITE$FAVICON" -o "$TMP/favicon.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-logo.png" "$TMP/logo.png"
  cmp -s "$APP/erpdevelopers/public/images/erpdevelopers-selected-favicon.png" "$TMP/favicon.png"

  echo "=== Public Cloudflare HTTPS GET checks ==="
  for route in / /training /insights /lets-talk /privacy /login /api/method/ping "$CSS" "$LOGIN_CSS" "$PORTAL_CSS" "$MEETING_CSS" "$LOGO" "$FAVICON"; do
    status="$(curl -fsSL --connect-timeout 5 --max-time 20 \
      -o /dev/null -w '%{http_code}' "https://$SITE$route")" || {
        echo "STOP: public route failed: $route"; exit 4;
      }
    echo "$status $route"
  done
  echo "PASS: EN/AR translation, native login, CSS, approved PNG and public routes"
)
