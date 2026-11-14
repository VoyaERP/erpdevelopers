/* Progressive website locale navigation; the visible link works without JS.
 * No AJAX, private APIs, User updates, cloned header or native picker override.
 */
(() => {
  "use strict";
  const header = document.querySelector("header.ed-nav");
  const control = header?.querySelector("[data-language-switch]");
  if (!control || header.dataset.languageBound === "1") return;
  const language = header.lang.toLowerCase().startsWith("ar") ? "ar" : "en";
  const target = control.dataset.languageSwitch;
  if (!["en", "ar"].includes(target)) return;
  header.dataset.languageBound = "1";

  const publicPaths = new Set([
    "/", "/erp-developers-home", "/training", "/events", "/projects",
    "/team-advice", "/insights", "/lets-talk", "/privacy",
    "/erp-development", "/erpnext-development", "/login",
  ]);
  const relative = url => url.pathname + url.search + url.hash;
  function updateSwitchURL() {
    const url = new URL(window.location.href);
    url.searchParams.set("_lang", target);
    control.href = relative(url); // Preserve current filters and fragment.
  }
  updateSwitchURL();
  window.addEventListener("hashchange", updateSwitchURL);

  function prepareLink(event) {
    if (event.defaultPrevented || (event.type === "auxclick" && event.button !== 1)) return;
    const anchor = event.target.closest?.("a[href]");
    if (!anchor || !anchor.closest(".ed-site") || anchor.hasAttribute("download")) return;
    if (anchor === control) {
      updateSwitchURL();
      // Frappe reads this cookie for Guests; _lang also works for signed-in users.
      try {
        document.cookie = `preferred_language=${target}; Path=/; SameSite=Lax${location.protocol === "https:" ? "; Secure" : ""}`;
      } catch (_) { /* Cookie restrictions must not prevent native _lang navigation. */ }
      return;
    }
    const href = anchor.getAttribute("href");
    if (!href || href.startsWith("#")) return;
    let url;
    try { url = new URL(href, window.location.href); } catch (_) { return; }
    if (url.origin !== window.location.origin || !publicPaths.has(url.pathname)) return;
    // Keep explicit language destinations; otherwise retain this website locale.
    if (!["en", "ar"].includes(url.searchParams.get("_lang"))) {
      url.searchParams.set("_lang", language);
      anchor.href = relative(url);
    }
    // Normal browser navigation, target/modifier behavior and fragments are kept.
  }
  document.addEventListener("click", prepareLink, true);
  document.addEventListener("auxclick", prepareLink, true);

  // Existing GET directory filters must not reset a signed-in user's page locale.
  document.querySelectorAll('.ed-site form[method="get" i]').forEach(form => {
    let action;
    try { action = new URL(form.getAttribute("action") || location.href, location.href); } catch (_) { return; }
    if (action.origin !== location.origin || !publicPaths.has(action.pathname)) return;
    let input = form.querySelector('input[name="_lang"]');
    if (input && input.type !== "hidden") return;
    if (!input) {
      input = document.createElement("input");
      input.type = "hidden";
      input.name = "_lang";
      form.appendChild(input);
    }
    input.value = language;
  });
})();
