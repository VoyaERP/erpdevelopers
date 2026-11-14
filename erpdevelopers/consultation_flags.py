"""Cheap, read-only site flag for public consultation page rendering.

The public GET page must not import guest POST endpoints or CRM dependencies.
"""
from erpdevelopers.branding import EXPECTED_SITE


def booking_open():
    import frappe
    from frappe.utils import cint

    return (
        frappe.local.site == EXPECTED_SITE
        and cint(frappe.conf.get("erpdev_consultation_open", 0)) == 1
    )
