/* Curators manage public/private editorial playlists without leaking
 * unpublished YouTube links to website visitors. Server enforces privacy.
 */
frappe.ui.form.on("ERP Developers Playlist", {
  refresh(frm) {
    sync_playlist_visibility(frm);
  },
  visibility(frm) {
    sync_playlist_visibility(frm);
  },
});

function sync_playlist_visibility(frm) {
  const private_record = frm.doc.visibility === "Private";
  frm.set_df_property("published", "read_only", private_record ? 1 : 0);
  frm.set_df_property(
    "published",
    "description",
    private_record
      ? __("Private playlists remain available to authorized Desk curators only.")
      : __("Enable only after approving the content for the public Training page.")
  );
  if (private_record && frm.doc.published) {
    frm.set_value("published", 0);
  }
}
