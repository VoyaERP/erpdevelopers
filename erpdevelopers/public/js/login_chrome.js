/* ERP Developers website presentation on Frappe v16's native /login.
   No login form duplication, request interception, 2FA override or auth logic. */
(() => {
  "use strict";

  const ICON = "/assets/erpdevelopers/images/erp-mark.svg";
  const copy = {
    en: {
      home: "Home",
      vision: "Vision",
      ecosystem: "Ecosystem",
      ai: "AI & Innovation",
      signIn: "Sign in",
      navigation: "Main navigation",
      skip: "Skip to sign in",
      asideLabel: "ERP Developers technology community",
      eyebrow: "ENGAGE. REASON. PROGRESS.",
      title: "A connected space for people and technology.",
      description: "Discover knowledge, build expertise and grow through collaboration. One technology community, without vendor boundaries.",
      engage: "Engage",
      engageDesc: "Connect people",
      reason: "Reason",
      reasonDesc: "Think intelligently",
      progress: "Progress",
      progressDesc: "Create impact",
      footer: "Technology grows stronger together.",
      copyright: "All rights reserved"
    },
    ar: {
      home: "الرئيسية",
      vision: "رؤيتنا",
      ecosystem: "المنصة",
      ai: "الذكاء والابتكار",
      signIn: "تسجيل الدخول",
      navigation: "القائمة الرئيسية",
      skip: "انتقل إلى تسجيل الدخول",
      asideLabel: "مجتمع ERP Developers التقني",
      eyebrow: "ENGAGE. REASON. PROGRESS.",
      title: "مساحة تجمع الخبرات والأفكار والتقنيات.",
      description: "تواصل مع الخبراء، وطوّر مهاراتك، وشارك المعرفة في مجتمع تقني لا يرتبط بنظام أو شركة واحدة.",
      engage: "Engage",
      engageDesc: "تعاون وتواصل",
      reason: "Reason",
      reasonDesc: "تفكير ذكي",
      progress: "Progress",
      progressDesc: "تطور وتأثير",
      footer: "التكنولوجيا أقوى بالتعاون.",
      copyright: "جميع الحقوق محفوظة"
    }
  };

  function element(tag, className, label) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (typeof label === "string") node.textContent = label;
    return node;
  }

  function link(href, label, className) {
    const node = element("a", className, label);
    node.href = href;
    return node;
  }

  function brand() {
    const a = link("/", "", "ed-login-brand");
    a.setAttribute("aria-label", "ERP Developers");
    const img = element("img", "ed-login-brand-image");
    img.src = ICON;
    img.width = 43;
    img.height = 43;
    img.alt = "";
    img.setAttribute("aria-hidden", "true");
    const name = element("span", "ed-login-brand-name");
    name.append(element("strong", "", "ERP"), element("span", "", "Developers"));
    a.append(img, name);
    return a;
  }

  function header(t) {
    const outer = element("header", "ed-login-header");
    const inner = element("div", "ed-login-header-inner");
    const nav = element("nav", "ed-login-nav");
    nav.setAttribute("aria-label", t.navigation);
    [
      ["/", t.home],
      ["/#vision", t.vision],
      ["/#ecosystem", t.ecosystem],
      ["/#ai", t.ai]
    ].forEach(([href, label]) => nav.appendChild(link(href, label)));
    const current = element("span", "ed-login-current", t.signIn);
    current.setAttribute("aria-current", "page");
    inner.append(brand(), nav, current);
    outer.appendChild(inner);
    return outer;
  }

  function story(t) {
    const aside = element("aside", "ed-login-story");
    aside.setAttribute("aria-label", t.asideLabel);
    const content = element("div", "ed-login-story-content");
    content.append(
      element("p", "ed-login-story-eyebrow", t.eyebrow),
      element("h2", "ed-login-story-title", t.title),
      element("p", "ed-login-story-description", t.description)
    );
    const values = element("div", "ed-login-values");
    [
      [t.engage, t.engageDesc],
      [t.reason, t.reasonDesc],
      [t.progress, t.progressDesc]
    ].forEach(([name, detail]) => {
      const item = element("div", "ed-login-value");
      item.append(element("strong", "", name), element("small", "", detail));
      values.appendChild(item);
    });
    content.appendChild(values);
    aside.appendChild(content);
    return aside;
  }

  function footer(t) {
    const outer = element("footer", "ed-login-footer");
    const inner = element("div", "ed-login-footer-inner");
    const wordmark = element("p", "ed-login-footer-brand");
    wordmark.append(element("strong", "", "ERP"), element("span", "", "Developers"));
    const summary = element("p", "ed-login-footer-summary", t.footer);
    const rights = element(
      "p", "ed-login-footer-rights",
      t.copyright + " © " + String(new Date().getFullYear())
    );
    inner.append(wordmark, summary, rights);
    outer.appendChild(inner);
    return outer;
  }

  function render() {
    if ((window.location.pathname.replace(/\/+$/, "") || "/") !== "/login") return;
    const page = document.getElementById("page-login");
    if (!page || document.body.dataset.edLoginEnhanced === "1") return;
    const wrapper = page.querySelector(".page-content-wrapper");
    if (!wrapper) return; // Leave Frappe's native login untouched on markup changes.

    const lang = (document.documentElement.lang || "en").toLowerCase().split("-")[0];
    const arabic = lang === "ar";
    const t = arabic ? copy.ar : copy.en;

    document.body.classList.add("ed-login-website");
    document.body.dataset.edLoginEnhanced = "1";
    const top = header(t);
    top.dir = arabic ? "rtl" : "ltr";
    document.body.insertBefore(top, page);

    const skip = link("#page-login", t.skip, "ed-login-skip");
    top.before(skip);
    const aside = story(t);
    aside.dir = arabic ? "rtl" : "ltr";
    wrapper.insertBefore(aside, wrapper.firstChild);

    const bottom = footer(t);
    bottom.dir = arabic ? "rtl" : "ltr";
    document.body.appendChild(bottom);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render, { once: true });
  } else {
    render();
  }
})();
