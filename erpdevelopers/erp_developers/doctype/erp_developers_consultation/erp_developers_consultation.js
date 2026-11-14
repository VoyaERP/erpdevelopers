// Native Desk action. Never creates a Lead from a public visitor session.
frappe.ui.form.on("ERP Developers Consultation", {
  refresh(frm) {
    if (frm.is_new() || frm.doc.lead || !frm.doc.email) return;
    if (!(frappe.user.has_role("Sales Manager") || frappe.user.has_role("System Manager"))) return;
    frm.add_custom_button(__("Create or Link ERPNext Lead"), () => {
      if (frm.is_dirty()) {
        frappe.msgprint(__("Save this request before creating a CRM Lead."));
        return;
      }
      frappe.call({
        method: "erpdevelopers.appointments.create_or_link_lead",
        args: { consultation_name: frm.doc.name },
        freeze: true,
        freeze_message: __("Linking CRM Lead..."),
        callback(r) {
          if (r.message && r.message.lead) {
            frappe.show_alert({message: __("CRM Lead linked"), indicator: "green"});
            frm.reload_doc();
          }
        },
      });
    }, __("CRM"));
  },
});
