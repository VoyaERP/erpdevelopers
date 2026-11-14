/* Native document saves enforce permissions and server-side public review. */
frappe.ui.form.on("ERP Developers Publication", {
  refresh(frm) {
    if (frm.is_new() || !frm.perm?.[0]?.write) return;
    const published = Boolean(Number(frm.doc.published));
    frm.add_custom_button(published ? __("Unpublish") : __("Publish"), async () => {
      await frm.set_value("published", published ? 0 : 1);
      await frm.save();
    }, __("Publication"));
    if (published && frm.doc.public_reviewed) {
      const route = frm.doc.publication_type === "Project" ? "/projects" : "/team-advice";
      frm.add_custom_button(__("View on website"), () => {
        window.open(route, "_blank", "noopener,noreferrer");
      });
    }
  }
});
