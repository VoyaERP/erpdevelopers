"""Concise plain-language intake notice; legal review required before activation."""
from erpdevelopers.public_pages import set_public_context

sitemap = 1


def get_context(context):
    set_public_context(
        context, slug="privacy", title="Consultation Privacy Notice",
        description="Read how consultation enquiries are collected and reviewed in ERP Developers' ERPNext-backed workflow.",
    )
