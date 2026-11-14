/* On-device FAQ guide. Never sends messages or accesses private ERPNext data. */
(() => {
  "use strict";
  function init() {
    const root = document.querySelector(".ed-assistant");
    if (!root) return;
    const opener = root.querySelector("[data-guide-toggle]");
    const closer = root.querySelector("[data-guide-close]");
    const panel = root.querySelector("#ed-guide-panel");
    const messages = root.querySelector("[data-guide-messages]");
    const questions = [...root.querySelectorAll("[data-guide-question]")];
    const setOpen = (open) => {
      panel.hidden = !open;
      opener.setAttribute("aria-expanded", String(open));
      if (open) closer.focus(); else opener.focus();
    };
    opener.addEventListener("click", () => setOpen(panel.hidden));
    closer.addEventListener("click", () => setOpen(false));
    root.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !panel.hidden) setOpen(false);
    });
    questions.forEach((button) => button.addEventListener("click", () => {
      const question = document.createElement("p");
      const answer = document.createElement("p");
      question.className = "ed-guide-question";
      answer.className = "ed-guide-answer";
      question.textContent = button.textContent.trim();
      answer.textContent = button.dataset.answer || "";
      messages.replaceChildren(question, answer);
    }));
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
