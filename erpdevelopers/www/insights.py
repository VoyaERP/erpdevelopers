"""Knowledge index linking to vetted external sources or native Web Pages."""
from erpdevelopers.catalog import public_catalog_topics, public_resources
from erpdevelopers.public_pages import set_public_context

sitemap = 1


def get_context(context):
    set_public_context(
        context, slug="insights", title="Insights & Practical Advice",
        description="Read practical technology insights, curated expert sources and architecture advice, with original articles published through Frappe Web Pages.",
    )
    context.resources = public_resources()
    context.topics = public_catalog_topics(context.resources)
