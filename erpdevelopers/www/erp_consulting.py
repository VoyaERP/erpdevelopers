"""Public, server-rendered bilingual ERP Developers topic guide."""
from erpdevelopers.guide_content import set_guide_context

sitemap = 1


def get_context(context):
    import frappe
    set_guide_context(context, "erp-consulting", frappe.local.lang)
