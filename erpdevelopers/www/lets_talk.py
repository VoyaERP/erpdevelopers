"""Native ERPNext appointment booking page; no guest writes during GET."""
from erpdevelopers.intake_rules import TOPICS
from erpdevelopers.meeting_status import booking_ready
from erpdevelopers.public_pages import set_public_context
from erpdevelopers.branding import versioned_public_asset

sitemap = 1


def get_context(context):
    set_public_context(
        context, slug="lets-talk", title="Let's Talk",
        description="Talk with ERP Developers about enterprise systems, solution architecture, integrations, training and partnerships. Choose an available meeting time with ERPNext.",
    )
    context.booking_enabled = booking_ready()
    context.topic_options = TOPICS
    context.meeting_css_url = versioned_public_asset("css/meeting.css")
    context.meeting_js_url = versioned_public_asset("js/meeting.js")
