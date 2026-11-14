"""Public, server-rendered ERPNext and Frappe editorial guide."""
from erpdevelopers.guide_content import set_guide_context

sitemap = 1


def get_context(context):
    import frappe
    set_guide_context(context, "erpnext-development", frappe.local.lang)
