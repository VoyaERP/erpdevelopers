/* Accessible client-only filtering: server sends only published curated rows. */
(() => {
  "use strict";
  function init() {
    document.querySelectorAll("[data-catalog-filter]").forEach((select) => {
      const target = document.querySelector(select.dataset.catalogFilter);
      if (!target) return;
      const cards = [...target.querySelectorAll("[data-catalog-topic]")];
      const counter = document.querySelector(select.dataset.countTarget || "");
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
