/* In-page playlist playback and published-catalog filtering. No external CTA. */
(() => {
  "use strict";
  function initPlaylistPlayer() {
    const controls = [...document.querySelectorAll("[data-playlist-open]")];
    const dialog = document.getElementById("ed-playlist-dialog");
    if (dialog?.dataset.playerBound === "1") return;
    const frame = dialog?.querySelector("[data-player-frame]");
    const title = dialog?.querySelector("#ed-playlist-dialog-title");
    const close = dialog?.querySelector("[data-player-close]");
    const status = dialog?.querySelector("[data-player-status]");
    const ready = Boolean(frame && title && close && typeof dialog.showModal === "function");
    const idPattern = /^[A-Za-z0-9_-]{12,64}$/;
    let lastFocus = null;
    const stopPlayback = () => {
      frame?.removeAttribute("src");
      if (status) status.hidden = true;
      if (lastFocus?.isConnected) lastFocus.focus();
      lastFocus = null;
    };
    controls.forEach(control => {
      control.disabled = !(ready && idPattern.test(control.dataset.playlistId || ""));
      control.addEventListener("click", event => {
        event.preventDefault();
        const id = control.dataset.playlistId || "";
        if (!ready || !idPattern.test(id)) return;
        const embed = new URL("https://www.youtube-nocookie.com/embed/videoseries");
        embed.searchParams.set("list", id);
        embed.searchParams.set("autoplay", "0");
        embed.searchParams.set("playsinline", "1");
        try {
          if (!dialog.open) dialog.showModal();
          lastFocus = control;
          title.textContent = control.dataset.playlistTitle || title.textContent;
          if (status) status.hidden = false;
          frame.src = embed.toString();
          close.focus();
        } catch (_) {
          stopPlayback();
          control.disabled = true;
        }
      });
    });
    if (!ready) return;
    dialog.dataset.playerBound = "1";
    dialog.addEventListener("close", stopPlayback);
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", event => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right ||
          event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
    frame.addEventListener("load", () => {
      // A loaded frame does not prove that YouTube allows a particular video.
      if (status && dialog.open && frame.getAttribute("src")) status.hidden = true;
    });
  }
  function init() {
    initPlaylistPlayer();
    document.querySelectorAll("[data-catalog-filter]").forEach(select => {
      const target = document.querySelector(select.dataset.catalogFilter);
      if (!target) return;
      const cards = [...target.querySelectorAll("[data-catalog-topic]")];
      const counter = select.dataset.countTarget ? document.querySelector(select.dataset.countTarget) : null;
      const filter = () => {
        let visible = 0;
        cards.forEach(card => {
          const show = !select.value || card.dataset.catalogTopic === select.value;
          card.hidden = !show;
          if (show) visible++;
        });
        if (counter) counter.textContent = String(visible);
      };
      select.addEventListener("change", filter);
      filter();
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true});
  else init();
})();
