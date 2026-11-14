/* One decorative site header + story around Frappe 16's ORIGINAL /login form.
 * Never clone auth inputs, intercept requests, or replace 2FA/session logic.
 */
(() => {
  "use strict";
  const LOGIN_PATH = "/login";
  const APPROVED_LOGO = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png";
  const NAV = [
    ["home", "/"],
    ["vision", "/#vision"],
    ["ecosystem", "/#ecosystem"],
    ["ai", "/#ai"],
  ];
  const copy = {
    en: {
      home:"Home", vision:"Vision", ecosystem:"Ecosystem", ai:"AI & Innovation",
      signIn:"Sign in", navigation:"Main navigation", skip:"Skip to sign in",
      asideLabel:"ERP Developers community", eyebrow:"ENGAGE. REASON. PROGRESS.",
      title:"A connected space for people and technology.",
      description:"Discover knowledge, build expertise and grow through collaboration — beyond any single ERP or vendor.",
      engage:"Engage", engageDesc:"Connect people",
      reason:"Reason", reasonDesc:"Think intelligently",
      progress:"Progress", progressDesc:"Create impact",
      footer:"Technology grows stronger together.", rights:"All rights reserved",
    },
    ar: {
      home:"الرئيسية", vision:"رؤيتنا", ecosystem:"المنظومة", ai:"الذكاء والابتكار",
      signIn:"تسجيل الدخول", navigation:"القائمة الرئيسية", skip:"انتقل إلى تسجيل الدخول",
      asideLabel:"مجتمع ERP Developers", eyebrow:"ENGAGE. REASON. PROGRESS.",
      title:"مساحة تجمع الأشخاص والخبرات والتقنيات.",
      description:"اكتشف المعرفة، وطوّر خبراتك، وانمُ من خلال التعاون دون التقيد بنظام ERP أو مورد محدد.",
      engage:"Engage", engageDesc:"التواصل والتعاون",
      reason:"Reason", reasonDesc:"التفكير والتحليل",
      progress:"Progress", progressDesc:"التطور والتأثير",
      footer:"التقنية أقوى بالتعاون.", rights:"جميع الحقوق محفوظة",
    },
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

  function brandImage(className, width, height, decorative) {
    const image = create("img", className);
    image.src = APPROVED_LOGO;
    image.width = width;
    image.height = height;
    image.alt = decorative ? "" : "ERP Developers — Engage. Reason. Progress.";
    if (decorative) image.setAttribute("aria-hidden", "true");
    return image;
  }

  function header(t) {
    const outer = create("header", "ed-login-header");
    const inner = create("div", "ed-login-header-inner");
    const brand = link("/", "", "ed-login-brand");
    brand.setAttribute("aria-label", "ERP Developers");
    brand.appendChild(brandImage("ed-login-brand-image", 207, 69, true));

    const navigation = create("nav", "ed-login-nav");
    navigation.setAttribute("aria-label", t.navigation);
    for (const [key, href] of NAV) {
      navigation.appendChild(link(href, t[key]));
    }

    const current = create("span", "ed-login-current", t.signIn);
    current.setAttribute("aria-current", "page");
    inner.append(brand, navigation, current);
    outer.appendChild(inner);
    return outer;
  }

  function story(t) {
    const aside = create("aside", "ed-login-story");
    aside.setAttribute("aria-label", t.asideLabel);
    const content = create("div", "ed-login-story-content");
    content.append(
      create("p", "ed-login-story-eyebrow", t.eyebrow),
      create("h2", "ed-login-story-title", t.title),
      create("p", "ed-login-story-description", t.description),
    );
    const values = create("div", "ed-login-values");
    for (const [name, description] of [
      [t.engage, t.engageDesc],
      [t.reason, t.reasonDesc],
      [t.progress, t.progressDesc],
    ]) {
      const item = create("div", "ed-login-value");
      item.append(create("strong", "", name), create("small", "", description));
      values.appendChild(item);
    }
    content.appendChild(values);
    aside.appendChild(content);
    return aside;
  }

  function footer(t) {
    const outer = create("footer", "ed-login-footer");
    const inner = create("div", "ed-login-footer-inner");
    const brand = create("a", "ed-login-footer-brand");
    brand.href = "/";
    brand.setAttribute("aria-label", "ERP Developers");
    brand.appendChild(brandImage("ed-login-footer-logo", 154, 51, true));

    const summary = create("p", "ed-login-footer-summary", t.footer);
    const rights = create(
      "p", "ed-login-footer-rights",
      t.rights + " © " + String(new Date().getFullYear()),
    );
    inner.append(brand, summary, rights);
    outer.appendChild(inner);
    return outer;
  }

  function render() {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    if (path !== LOGIN_PATH) return;

    const page = document.getElementById("page-login");
    const wrapper = page && page.querySelector(".page-content-wrapper");
    if (!wrapper || !wrapper.querySelector("main")) return;

    // This guard also covers a duplicated/late-loaded script from a stale bundle.
    if (document.body.dataset.edLoginEnhanced === "1" ||
        document.querySelector(".ed-login-header")) return;

    const language = (document.documentElement.lang || "en")
      .toLowerCase().split(/[-_]/)[0];
    const t = copy[language] || copy.en;
    const direction = language === "ar" ? "rtl" : "ltr";
    const top = header(t);
    const bottom = footer(t);
    const aside = story(t);
    top.dir = bottom.dir = aside.dir = direction;

    // Move ONLY Frappe's existing language picker into our single header.
    // The original navbar will be hidden after enhancement, not duplicated.
    const picker = document.getElementById("language-switcher");
    if (picker) {
      picker.classList.add("ed-login-language");
      const select = picker.querySelector("select");
      if (select && !select.getAttribute("aria-label")) {
        select.setAttribute("aria-label", language === "ar" ? "اللغة" : "Language");
      }
      top.querySelector(".ed-login-current").before(picker);
    }

    // Decorate AROUND Frappe's own main; leave native auth forms untouched.
    const skip = link("#page-login", t.skip, "ed-login-skip");
    wrapper.prepend(aside);
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
