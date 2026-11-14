# Event URL correction and photos

## Evidence

The previous shared validator rejected every erp-developers.com URL and returned
one private-address error for HTTP, missing schemes, nonstandard ports and other
failures. The operator did not provide the exact rejected URL, so no particular
input is claimed to have been reproduced. This change covers those known cases.

## URL behavior

Event Official event URL and optional Source URL share one normalizer:
- Bare domains, www domains and HTTP links are saved as HTTPS.
- Public erp-developers.com pages are allowed. Own-site /desk, /app, /api,
  /private, /login and /me remain blocked, including encoded equivalents.
- Unicode domains use IDNA; Unicode paths and spaces are percent-encoded.
- IP literals, browser-style numeric IP aliases, private hostname suffixes,
  credentials, unsafe protocols, malformed hosts and nonstandard ports fail.
- Error messages name the field and the actual validation reason.
- Resource links retain their stricter HTTPS/external-only policy.

No DNS lookup or remote download occurs. HTTPS normalization does not prove that
the destination exists or supports TLS; the curator still verifies the official
source. This is not a reusable SSRF defense for server-side importers.

## Event photos

Use ERP Developers Event > Event photos > Cover image. Optional cover captions
are available in English/Arabic. Photo gallery supports up to eight ordered rows,
each with a native Attach Image field and English/Arabic caption. A missing cover
falls back to the first valid gallery photo. Save and keep the event Published
and region-relevant to show it in /events; no build/migrate is required per photo.

Native image uploads are explicitly public by default in these fields only.
Public files are accessible from upload even on a draft event. Upload only
material you are entitled to publish, never confidential or private images.
Private files are rejected, never automatically converted. Supported image
formats are JPG/JPEG, PNG, WebP and GIF, maximum 5 MiB and 24 megapixels each.
SVG, HTML, data URLs, external image URLs and private paths are rejected.

Save-time validation checks native File read permission, public status, file
size, containment under this site's public/files folder and real raster bytes.
The public directory uses two bounded batch queries at most for a page's media,
rechecks File privacy and skips deleted/private references. It never reads all
attachments or private Calendar Event files. Images without captions fall back
to the event title for alt text. A native expandable gallery needs no new public
JavaScript; pictures use lazy loading and keep poster proportions.

Removing a gallery row stops listing the photo after Save; it does not revoke
an existing public file URL. Use File Manager to remove/change the actual upload
when necessary. Making a File private removes it from new directory responses;
it cannot recall previously downloaded files or third-party caches.

## Release boundary

Deploy once using the existing backup-first updater to sync the new parent fields
and child DocType and compile translations. Run Python/Node and Chromium/Firefox
fixtures. No production data, published flags, old links, attachment privacy or
Frappe core files are changed automatically. Live native-upload and role UAT
remain required on the real Frappe site after deployment.
