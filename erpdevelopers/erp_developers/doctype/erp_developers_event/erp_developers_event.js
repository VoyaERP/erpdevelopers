/* Native saves enforce permissions and server validation; no public write API. */
frappe.ui.form.on("ERP Developers Event", {
  refresh(frm) {
    if (frm.is_new() || !frm.has_perm("write")) return;
    frm.add_custom_button(__(frm.doc.published ? "Unpublish" : "Publish"), async () => {
      await frm.set_value("published", frm.doc.published ? 0 : 1);
      await frm.save();
    }, __("Publication"));
    const statuses = (frm.get_docfield("event_status").options || "").split("\n");
    statuses.filter(status => status && status !== frm.doc.event_status).forEach(status => {
      frm.add_custom_button(__(status), async () => {
        await frm.set_value("event_status", status);
        await frm.save();
      }, __("Event status"));
    });
  },
});
