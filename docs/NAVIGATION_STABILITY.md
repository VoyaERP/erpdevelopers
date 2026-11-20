# Header refresh stability and mobile wrapping

## Source findings

The public header is a single server-rendered include. The FAQ script does not
clone or replace it. The previous brand.css explicitly applied display:none to
.ed-language-switcher.hide, while Frappe v16.56.0 website.js asynchronously fetched
languages and removed hide. The horizontal header redistributed space at that
point. This explains a reproducible layout-shift mechanism; it is not proof that
the reported live browser has no additional theme, Cloudflare or cache issue.

Frappe's native picker also writes document.documentElement.lang from a cookie or
navigator.language after rendering. The header now declares its actual rendered
lang and dir, so its copy does not flip typography/direction during that callback.
The existing native picker/change handler remains the only language script.
This does not modify Frappe core or claim to change its language resolution.

## Fix

Refactor the existing brand.css rules in place: reserve the language control's
width and height while hidden; give the logo explicit display dimensions; use
stable desktop logo/menu/tool tracks and equal link cells. On tablet/phone use
two header rows: logo plus native language/login controls, then the full-width
single-line horizontal link strip. Links remain reachable with keyboard focus
and horizontal scrolling in both directions. No second header, hamburger copy,
new production JavaScript, duplicate CSS override file, auth override or new
font file is added. The approved logo is unchanged.

Short nav/footer labels stay whole. Mobile CTAs get sufficient width rather than
squeezing two long labels beside each other. Decorative pills wrap as whole items
and CTA arrows cannot fall onto their own flex row. Paragraphs and long headings
still wrap; forcing all content to one line would clip translations.

## Regression boundary

Existing Python/Node/browser/schema checks remain. A dedicated browser fixture
restores the actual shared nav/footer (previous content fixtures omitted these),
loads the actual page templates/styles, and executes the Git-blob-pinned native
picker method through a small AJAX/DOM adapter. It first reproduces movement with
the exact old CSS, then measures delayed hydration and refresh at 320, 390, 540,
768, 1100, 1101 and 1440 CSS pixels in EN/AR on Home/Training/Events, Chromium and
Firefox. It checks single-line labels, no whole-page horizontal overflow, sticky
position and keyboard access to all links. It also tests native root-language
mismatch. External font responses and the surrounding Frappe shell are fixtures.
This is not a live browser trace, full Frappe integration test or claim of zero CLS
from every asset on the website. The public site could not be fetched from the
assistant environment during this review.

Deploy using the existing pinned complete deployment runner. This release builds
on the previous event URL schema correction; do not revert that correction.
Use a hard refresh and check both languages on the live site after deployment.
