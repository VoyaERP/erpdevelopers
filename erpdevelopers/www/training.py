"""Public curated YouTube training; not an LMS or automated YouTube feed."""
from erpdevelopers.catalog import public_catalog_topics, public_playlists
from erpdevelopers.public_pages import set_public_context

sitemap = 1


def get_context(context):
    set_public_context(
        context, slug="training", title="Training Playlists",
        description="Explore reviewed YouTube playlists about ERP, solution architecture, development, cloud, data and security. Curated learning, with an LMS planned.",
    )
    context.playlists = public_playlists()
    context.topics = public_catalog_topics(context.playlists)
