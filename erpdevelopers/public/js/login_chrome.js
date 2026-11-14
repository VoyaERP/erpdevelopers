/* ERP Developers chrome for the native Frappe /login page.
 * Decorative siblings only: never replace or intercept the authentication form.
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
      home: "Home", vision: "Vision", ecosystem: "Ecosystem",
      ai: "AI & Innovation", signIn: "Sign in",
      navigation: "Main navigation", skip: "Skip to sign in",
      footer: "A community for people, knowledge and technology.",
      rights: "All rights reserved",
    },
    ar: {
      home: "الرئيسية", vision: "رؤيتنا", ecosystem: "المنصة",
      ai: "الذكاء والابتكار", signIn: "تسجيل الدخول",
      navigation: "القائمة الرئيسية", skip: "انتقل إلى تسجيل الدخول",
      footer: "مجتمع يجمع الخبرات والمعرفة والتقنيات.",
      rights: "جميع الحقوق محفوظة",
    },
  };

  function create(tag, className, label) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (typeof label === "string") element.textContent = label;
    return element;
  }

  function link(href, label, className) {
    const anchor = create("a", className, label);
    anchor.href = href;
    return anchor;
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
    brand.appendChild(brandImage("ed-login-brand-image", 216, 72, true));

    const navigation = create("nav", "ed-login-nav");
    navigation.setAttribute("aria-label", t.navigation);
    for (const [name, href] of NAV) {
      navigation.appendChild(link(href, t[name]));
    }

    const current = create("span", "ed-login-current", t.signIn);
    current.setAttribute("aria-current", "page");
    inner.append(brand, navigation, current);
    outer.appendChild(inner);
    return outer;
  }

  function footer(t) {
    const outer = create("footer", "ed-login-footer");
    const inner = create("div", "ed-login-footer-inner");
    const brand = create("div", "ed-login-footer-brand");
    brand.appendChild(brandImage("ed-login-footer-logo", 155, 52, false));

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
    if (!page || !page.querySelector(".page-content-wrapper")) return;
    if (document.body.dataset.edLoginEnhanced === "1") return;

    const language = (document.documentElement.lang || "en")
      .toLowerCase().split(/[-_]/)[0];
    const t = copy[language] || copy.en;
    const direction = language === "ar" ? "rtl" : "ltr";
    const skip = link("#page-login", t.skip, "ed-login-skip");
    const top = header(t);
    const bottom = footer(t);
    top.dir = direction;
    bottom.dir = direction;

    // Only move the website's language selector, never the native login form.
    const picker = document.getElementById("language-switcher");
    if (picker) {
      const select = picker.querySelector("select");
      if (select && !select.getAttribute("aria-label")) {
        select.setAttribute("aria-label", language === "ar" ? "اللغة" : "Language");
      }
      picker.classList.add("ed-login-language");
      top.querySelector(".ed-login-current").before(picker);
    }

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
