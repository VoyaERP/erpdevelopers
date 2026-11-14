# Projects, Team Advice and the minimal footer

## Routes and scope

/projects is a curated public project showcase. /team-advice contains recommendations
and articles authored by the team, not an employee directory. Both use one native
ERP Developers Publication DocType, one renderer and one shared template. No ERPNext
Project, Task, Customer, Employee or User records are imported or published.
No example projects, client claims, team identities or advice articles are seeded.

The shared footer keeps its existing logo and exactly three text links: Let's Talk
(/lets-talk#meeting-start), Team Login (/login?redirect-to=/desk), and Back to top
(#top on the current page). The new pages are in the main header, not the footer.
The stable reserved language-picker slot is retained. The eight-link header uses
its lower scrolling row below 1361px instead of compressing labels.

## Publishing through Desk

Website Manager or System Manager: search for ERP Developers Publication, then New.
Choose Publication type Project or Team Advice and select a Topic. Enter Title,
Summary and Content in English. Content is plain text; paragraphs are preserved
and HTML is escaped. Add the Arabic title, summary and content together for a full
Arabic card. Without a complete Arabic version, that card explicitly uses English
language/direction rather than mixing partially translated prose.

Project entries can include Industry and Technologies. Team Advice requires an
explicit public author name when publishing; no private user's profile/email is
looked up. Optional public cover uploads reuse the existing image security checks.
They are public from upload even if the publication is a draft; upload no private
client material. Unpublishing does not revoke a previously public file URL.

Review text, client-name permissions and image rights; enable Approved for public
sharing. Save, then Publication > Publish (or check Published and save). Unpublish
uses the same permission-checked save. Public queries always require Published=1,
Approved for public sharing=1 and the matching publication type. Internal notes
are never selected. Public visitors get no generic DocType read/write permission.

The public pages include topic filtering, bounded 12-card pagination, native
expandable full text, and an explicit consultation link. Manage publications is
shown only to authenticated users with read access. No background task or new
public navigation script is added. The stylesheet is content-fingerprinted.

## Deployment and validation

The previous navigation fix and URL-field migration are retained. Deploy once
with the existing pinned backup-first deployment runner to sync the new DocType
and build translations/assets. Subsequent content saves require no rebuild or
migration; these directories use uncached server-rendered data.

Pure tests cover review gates, required fields, text limits, query filters,
pagination, language fallback, privacy-safe media, DocType roles and the footer.
Chromium/Firefox tests render the real new controllers/templates with a fake DB
and the actual shared header/footer. EN/AR are checked at 320,390,768,1360,1361,1440px.
These are not live Frappe upload/login/publishing integration tests. After deploying,
check a draft, a published project and published advice as both Guest and editor.
