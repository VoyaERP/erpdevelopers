"""Concise plain-language intake notice; legal review required before activation."""
from erpdevelopers.public_pages import set_public_context

sitemap = 1


def get_context(context):
    set_public_context(
        context, slug="privacy", title="Meeting Privacy Notice",
        description="Read how ERP Developers' native ERPNext meeting booking collects and handles appointment details and email verification.",
    )
