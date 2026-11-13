/* Native Frappe v16 /login enhancement.
 * Same safe method as Green Box: decorative brand chrome around the ORIGINAL form.
 * We never translate auth messages, reparent fields, replace forms or intercept requests.
 */
(() => {
  "use strict";

  const ICON = "/assets/erpdevelopers/images/erp-mark.svg";
  const copy = {
    en: {
      home: "Home", vision: "Vision", ecosystem: "Ecosystem",
      ai: "AI & Innovation", signIn: "Sign in",
      navigation: "Main navigation", skip: "Skip to sign in",
      footer: "A community for people, knowledge and technology.",
      rights: "All rights reserved"
    },
    ar: {
      home: "الرئيسية", vision: "رؤيتنا", ecosystem: "المنصة",
      ai: "الذكاء والابتكار", signIn: "تسجيل الدخول",
      navigation: "القائمة الرئيسية", skip: "انتقل إلى تسجيل الدخول",
      footer: "مجتمع يجمع الخبرات والمعرفة والتقنيات.",
      rights: "جميع الحقوق محفوظة"
    }
  };

  function create(tag, className, label) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (typeof label === "string") node.textContent = label;
    return node;
  }

  function link(href, label, className) {
    const node = create("a", className, label);
    node.href = href;
    return node;
  }

  function wordmark() {
    const name = create("span", "ed-login-brand-name");
    name.append(create("strong", "", "ERP"), create("span", "", "Developers"));
    return name;
  }

  function header(t) {
    const outer = create("header", "ed-login-header");
    const inner = create("div", "ed-login-header-inner");
    const brand = link("/", "", "ed-login-brand");
    brand.setAttribute("aria-label", "ERP Developers");
    const img = create("img", "ed-login-brand-image");
    img.src = ICON;
    img.width = 44;
    img.height = 44;
    img.alt = "";
    img.setAttribute("aria-hidden", "true");
    brand.append(img, wordmark());

    const nav = create("nav", "ed-login-nav");
    nav.setAttribute("aria-label", t.navigation);
    [
      ["/", t.home],
      ["/#vision", t.vision],
      ["/#ecosystem", t.ecosystem],
      ["/#ai", t.ai]
    ].forEach(([href, label]) => nav.appendChild(link(href, label)));

    const current = create("span", "ed-login-current", t.signIn);
    current.setAttribute("aria-current", "page");
    inner.append(brand, nav, current);
    outer.appendChild(inner);
    return outer;
  }

  function footer(t) {
    const outer = create("footer", "ed-login-footer");
    const inner = create("div", "ed-login-footer-inner");
    const brand = create("div", "ed-login-footer-brand");
    brand.append(wordmark(), create("small", "", "Engage. Reason. Progress."));
    const summary = create("p", "ed-login-footer-summary", t.footer);
    const rights = create(
      "p", "ed-login-footer-rights",
      t.rights + " © " + String(new Date().getFullYear())
    );
    inner.append(brand, summary, rights);
    outer.appendChild(inner);
    return outer;
  }

  function render() {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    if (path !== "/login") return;
    const page = document.getElementById("page-login");
    if (!page || !page.querySelector(".page-content-wrapper")) return;
    if (document.body.dataset.edLoginEnhanced === "1") return;

    const language = (document.documentElement.lang || "en")
      .toLowerCase().split("-")[0];
    const t = language === "ar" ? copy.ar : copy.en;
    const direction = language === "ar" ? "rtl" : "ltr";
    const skip = link("#page-login", t.skip, "ed-login-skip");
    const top = header(t);
    const bottom = footer(t);
    top.dir = direction;
    bottom.dir = direction;

    // Only add siblings to body. No changes inside native Frappe login DOM.
    document.body.classList.add("ed-login-website");
    document.body.dataset.edLoginEnhanced = "1";
    document.body.prepend(skip, top);
    document.body.appendChild(bottom);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render, { once: true });
  } else {
    render();
  }
})();
