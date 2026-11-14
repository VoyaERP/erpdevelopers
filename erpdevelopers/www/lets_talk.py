"""Consultation request page: enquiry only, no unverified calendar booking."""
from erpdevelopers.public_pages import set_public_context

sitemap = 1


def get_context(context):
    from erpdevelopers.appointments import booking_open

    set_public_context(
        context, slug="lets-talk", title="Let's Talk",
        description="Request a conversation about ERP, solution architecture, training, integrations and digital transformation. Meeting times are confirmed by our team.",
    )
    context.booking_enabled = booking_open()
