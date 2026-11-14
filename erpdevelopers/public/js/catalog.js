/* Accessible client-only filtering: server sends only published curated rows. */
(() => {
  "use strict";
  // Progressive enhancement: the original anchor always points to the safe,
  // server-validated YouTube playlist. A failed/missing script or unsupported
  // HTMLDialogElement must NEVER leave the Watch button without an action.
  // No iframe request occurs before a visitor explicitly clicks Watch.
  function initPlaylistPlayer() {
    const dialog = document.getElementById("ed-playlist-dialog");
    if (!dialog || typeof dialog.showModal !== "function") return;
    const frame = dialog.querySelector("[data-player-frame]");
    const title = dialog.querySelector("#ed-playlist-dialog-title");
    const external = dialog.querySelector("[data-player-external]");
    const close = dialog.querySelector("[data-player-close]");
    if (!frame || !title || !external || !close) return;

    const idPattern = /^[A-Za-z0-9_-]{12,64}$/;
    let lastFocus = null;

    const stopPlayback = () => {
      frame.removeAttribute("src");
      if (lastFocus && lastFocus.isConnected) lastFocus.focus();
      lastFocus = null;
    };
    dialog.addEventListener("close", stopPlayback);
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", event => {
      if (event.target === dialog) dialog.close();
    });

    document.querySelectorAll("[data-playlist-open]").forEach(link => {
      link.addEventListener("click", event => {
        const id = link.dataset.playlistId || "";
        if (!idPattern.test(id)) return; // native YouTube link still works

        const watch = new URL("https://www.youtube.com/playlist");
        watch.searchParams.set("list", id);

        // YouTube's Share > Embed playlist form. The old /embed?listType=
        // form can fail to resolve playlists in privacy-enhanced embeds.
        const embed = new URL("https://www.youtube-nocookie.com/embed/videoseries");
        embed.searchParams.set("list", id);
        embed.searchParams.set("autoplay", "0");
        embed.searchParams.set("playsinline", "1");

        try {
          dialog.showModal();
        } catch (_) {
          return; // opening a new-tab YouTube playlist remains possible
        }
        event.preventDefault(); // only intercept when the dialog actually opened
        lastFocus = link;
        title.textContent = link.dataset.playlistTitle || "Video playlist";
        external.href = watch.toString();
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
