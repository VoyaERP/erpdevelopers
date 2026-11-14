/* Accessible client-only filtering: server sends only published curated rows. */
(() => {
  "use strict";
  // Only approved public playlist IDs reach the DOM. Validate again before
  // assigning an iframe src, and never load YouTube before an explicit click.
  function initPlaylistPlayer() {
    const dialog = document.getElementById("ed-playlist-dialog");
    if (!dialog) return;
    const buttons = [...document.querySelectorAll("[data-playlist-open]")];
    const frame = dialog.querySelector("[data-player-frame]");
    const title = dialog.querySelector("#ed-playlist-dialog-title");
    const external = dialog.querySelector("[data-player-external]");
    const close = dialog.querySelector("[data-player-close]");
    const idPattern = /^[A-Za-z0-9_-]{12,64}$/;
    if (typeof dialog.showModal !== "function") {
      buttons.forEach(button => { button.hidden = true; });
      return;
    }
    let lastFocus = null;
    const stopPlayback = () => {
      frame.removeAttribute("src");
      if (lastFocus && lastFocus.isConnected) lastFocus.focus();
    };
    dialog.addEventListener("close", stopPlayback);
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", event => {
      if (event.target === dialog) dialog.close();
    });
    buttons.forEach(button => {
      button.addEventListener("click", () => {
        const id = button.dataset.playlistId || "";
        if (!idPattern.test(id)) return;
        const watch = new URL("https://www.youtube.com/playlist");
        watch.searchParams.set("list", id);
        const embed = new URL("https://www.youtube-nocookie.com/embed");
        embed.searchParams.set("listType", "playlist");
        embed.searchParams.set("list", id);
        embed.searchParams.set("autoplay", "0");
        title.textContent = button.dataset.playlistTitle || "Video playlist";
        external.href = watch.toString();
        lastFocus = button;
        dialog.showModal();
        frame.src = embed.toString();
        close.focus();
      });
    });
  }

  function init() {
    initPlaylistPlayer();
    document.querySelectorAll("[data-catalog-filter]").forEach((select) => {
      const target = document.querySelector(select.dataset.catalogFilter);
      if (!target) return;
      const cards = [...target.querySelectorAll("[data-catalog-topic]")];
      const counterSelector = select.dataset.countTarget;
      const counter = counterSelector ? document.querySelector(counterSelector) : null;
      const filter = () => {
        let visible = 0;
        cards.forEach((card) => {
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
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
